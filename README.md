# Ekeko

## Setup

### Create image 

`podman build -t arch-ekeko:latest /path/to/arch-ekeko`

> Note: you can replace podman with docker

#### Running with distrobox

Once this image is create you can then create a distrobox image.

`distrobox create --image arch-ekeko:latest --name arch-ekeko`

which you can then run with

`distrobox enter arch-ekeko`
