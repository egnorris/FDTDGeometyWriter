#FDTDGeometryWriter
#Evan Norris
#May 2024

# Allow usage of commandline argument to signal first time usage
if size(ARGS)[1] != 0
    if ARGS[1] == "true"
        println("Running First Time Configuration")
        import Pkg
        Pkg.add(["JSON", "Images", "FileIO", "Plots"])

    elseif ARGS[1] == "false"
        println("Skipping First Time Configuration")
        println("Please Note that This Flag is Not Needed for Future Usage")
    end
end
using JSON, Images, FileIO, Plots


function check_dictionary_key(dictionary, key, default, entry)
    if haskey(dictionary, key) == false
        @warn string("Material ",entry," does not have an entry for ", key, " \nThe entry from Material 1 will be used")
        return default
    else
        return dictionary[key]
    end
end

function LoadParams(path)
    j = open(JSON.parse, path)
    key_strings = ["image-path", "material", "thickness", "y-placement"]
    default = []
    for i = 1:length(key_strings)
        push!(default,j[1][key_strings[i]])
    end
    number_of_materials = length(j)
    mat = []
    for i = 1:number_of_materials
        mat1 = []
        for k = 1:length(default)
            push!(mat1,check_dictionary_key(j[i], key_strings[k], default[k], i))
        end
        push!(mat, Dict("image-path"=>mat1[1], "material"=>mat1[2], "thickness"=>mat1[3], "y-placement"=>mat1[4]))
    end
    return mat
end

function LoadINI(path)
    j = open(JSON.parse, "pphinfoini.json")
    return [j["Domain Size"], j["Step Size"]]
end

function load_image(path)
    img = load(path)
    ny, nx = size(img)
    arr = ones(ny,nx)
    for i = 1:nx
        for j = 1:ny
            if img[j,i].r == img[j,i].g == img[j,i].b && img[j,i].r == 1.0N0f8
                arr[j,i] = 0
            end
        end
    end
    return arr
end

function get_boundary_coordinates(reference)
    ny, nx = size(reference)
    left_boundary_coordinates = []
    right_boundary_coordinates = []
    for iy = 1:ny
        for ix = 1:nx
            current_pixel = reference[iy,ix]
            if ix > 1
                previous_pixel = reference[iy,ix-1]
                    if current_pixel == 1 && previous_pixel == 0
                        #println("left edge at (",ix, ",", iy, ")")
                        push!(left_boundary_coordinates,[ix,iy])
                    end
            end
            if ix < nx
                next_pixel = reference[iy,ix+1]
                if current_pixel == 1 && next_pixel == 0
                        #println("right edge at (",ix, ",", iy, ")")
                        push!(right_boundary_coordinates,[ix,iy])
                end
            end


        end
    end
    return [left_boundary_coordinates, right_boundary_coordinates]
end

function get_geometry_data(left_boundary_coordinates, right_boundary_coordinates)
    center_points = zeros(length(left_boundary_coordinates),2)
    geometry_length = zeros(length(left_boundary_coordinates))
    for i = 1:length(left_boundary_coordinates)
        Lx, y = left_boundary_coordinates[i]
        Rx, _ = right_boundary_coordinates[i]
        center_points[i,:] = [(Rx+Lx)/2, y]
        geometry_length[i] = sqrt((Rx - Lx)^2)
    end
    return [center_points, geometry_length]
end

function write_geometry(filename; pixel_size, xz_coordinate,y_coordinate, block_length,thickness,material, append = false, final = false)
    geometry_string = string("{\n
                         \"shape\": \"Rectangle\",
                         \"radius\": ",pixel_size,",
                         \"length\": ",pixel_size,",
                         \"width\": ",block_length,",
                         \"thickness\": ",thickness,",
                         \"material\": \"",material,"\",
                         \"position\": [",xz_coordinate[1],",",y_coordinate,",",xz_coordinate[2],"] \n}")
    if append == false
        open("geometry.json", "w") do file
            write(file, "[")
            write(file, geometry_string)
            write(file, ",\n")
        end
    elseif append == true && final == false
        open("geometry.json", "a") do file
            write(file, geometry_string)
            write(file, ",\n")
        end
    elseif append == true && final == true
        open("geometry.json", "a") do file
            write(file, geometry_string)
            write(file, "\n]")
        end
    end
end

function generate_geometry_file(materials, pixel_size)
    println(pixel_size)
    write_geometry(
        "geometry.json",
        xz_coordinate = materials[1]["xz-coordinates"][1,:],
        y_coordinate = materials[1]["y-coordinate"],
        thickness = materials[1]["thickness"],
        material = materials[1]["material"],
        block_length = materials[1]["block-lengths"][1],
        pixel_size = pixel_size
        )
    for k = 2:length(materials)
        write_geometry(
            "geometry.json",
            xz_coordinate = materials[k]["xz-coordinates"][1,:],
            y_coordinate = materials[k]["y-coordinate"],
            thickness = materials[k]["thickness"],
            material = materials[k]["material"],
            block_length = materials[k]["block-lengths"][1],
            append = true,
            pixel_size = pixel_size
            )
    end

    for i = 1:length(materials[1]["block-lengths"])-1
        for k = 1:length(materials)
            write_geometry(
                "geometry.json",
                xz_coordinate = materials[k]["xz-coordinates"][i,:],
                y_coordinate = materials[k]["y-coordinate"],
                thickness = materials[k]["thickness"],
                material = materials[k]["material"],
                block_length = materials[k]["block-lengths"][i],
                append = true,
                pixel_size = pixel_size
                )
        end
    end
    for k = 2:length(materials)
        write_geometry(
            "geometry.json",
            xz_coordinate = materials[k]["xz-coordinates"][end,:],
            y_coordinate = materials[k]["y-coordinate"],
            thickness = materials[k]["thickness"],
            material = materials[k]["material"],
            block_length = materials[k]["block-lengths"][end],
            append = true,
            pixel_size = pixel_size
            )
    end
    write_geometry(
            "geometry.json",
            xz_coordinate = materials[1]["xz-coordinates"][end,:],
            y_coordinate = materials[1]["y-coordinate"],
            thickness = materials[1]["thickness"],
            material = materials[1]["material"],
            block_length = materials[1]["block-lengths"][end],
            append = true,
            final = true,
            pixel_size = StepSize[1]
            )
end

Params = LoadParams("params.json")
DomainSize, StepSize = LoadINI("pphinfoini.json")
reference_images = []
println("The current configuration of pphinfoini.json is expecting:")
println("X-domain: ",DomainSize[1]," [nm]     Y-domain: ",DomainSize[2]," [nm]   Z-domain: ",DomainSize[3]," [nm]")
for i = 1:length(Params)
    path = Params[i]["image-path"]
    reference = load_image(path)
    nz, nx = size(reference)
    println("The Input Image for Material ", i," has the Following Dimensions:")
    println("X-domain: ",nx," [nm]     Z-domain: ",nz," [nm]")
    push!(reference_images, reference)
end
geometry_writer_input = []
for i = 1:length(reference_images)
    left_boundary_coordinates, right_boundary_coordinates = get_boundary_coordinates(reference_images[i])
    center_points, geometry_length = get_geometry_data(left_boundary_coordinates, right_boundary_coordinates)
    geometry_length = geometry_length
    println("Output geometry preview image to material_",i,"_geometry_preview.png")
    push!(geometry_writer_input,Dict(
            "material" => Params[i]["material"],
            "thickness" => Params[i]["thickness"], 
            "y-coordinate" => Params[i]["y-placement"], 
            "xz-coordinates" => center_points, 
            "block-lengths"=> geometry_length*StepSize[1]
            ) )
end

generate_geometry_file(geometry_writer_input, StepSize[1]);