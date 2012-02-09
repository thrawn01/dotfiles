

# Install Images
# ==============

# Upload an image to glance.
#
# The default image is a small ***TTY*** testing image, which lets you login
# the username/password of root/password.
#
# TTY also uses cloud-init, supporting login via keypair and sending scripts as
# userdata.  See https://help.ubuntu.com/community/CloudInit for more on cloud-init
#
# Override ``IMAGE_URLS`` with a comma-separated list of uec images.
#
#  * **natty**: http://uec-images.ubuntu.com/natty/current/natty-server-cloudimg-amd64.tar.gz
#  * **oneiric**: http://uec-images.ubuntu.com/oneiric/current/oneiric-server-cloudimg-amd64.tar.gz
set -o xtrace

FILES=/tmp/publish-images

# Create a directory for the image tarballs.
mkdir -p $FILES/images
# Copy the image to our temp dir
cp $1 $FILES

IMAGE_FNAME=`basename "$1"`
KERNEL=""
RAMDISK=""
case "$IMAGE_FNAME" in
    *.tar.gz|*.tgz)
        # Extract ami and aki files
        [ "${IMAGE_FNAME%.tar.gz}" != "$IMAGE_FNAME" ] &&
            IMAGE_NAME="${IMAGE_FNAME%.tar.gz}" ||
            IMAGE_NAME="${IMAGE_FNAME%.tgz}"
        xdir="$FILES/images/$IMAGE_NAME"
        rm -Rf "$xdir";
        mkdir "$xdir"
        tar -zxf $FILES/$IMAGE_FNAME -C "$xdir"
        KERNEL=$(for f in "$xdir/"*-vmlinuz*; do
                 [ -f "$f" ] && echo "$f" && break; done; true)
        RAMDISK=$(for f in "$xdir/"*-initrd*; do
                 [ -f "$f" ] && echo "$f" && break; done; true)
        IMAGE=$(for f in "$xdir/"*.img; do
                 [ -f "$f" ] && echo "$f" && break; done; true)
        [ -n "$IMAGE_NAME" ]
        IMAGE_NAME=$(basename "$IMAGE" ".img")
        ;;
    *.img)
        IMAGE="$FILES/$IMAGE_FNAME";
        IMAGE_NAME=$(basename "$IMAGE" ".img")
        ;;
    *.img.gz)
        IMAGE="$FILES/${IMAGE_FNAME}"
        IMAGE_NAME=$(basename "$IMAGE" ".img.gz")
        ;;
    *) echo "Do not know what to do with $IMAGE_FNAME"; false;;
esac

# Use glance client to add the kernel the root filesystem.
# We parse the results of the first upload to get the glance ID of the
# kernel for use when uploading the root filesystem.
KERNEL_ID=""; RAMDISK_ID="";
if [ -n "$KERNEL" ]; then
    RVAL=`glance add -A $EC2_SECRET_KEY name="$IMAGE_NAME-kernel" is_public=true container_format=aki disk_format=aki < "$KERNEL"`
    KERNEL_ID=`echo $RVAL | cut -d":" -f2 | tr -d " "`
fi
if [ -n "$RAMDISK" ]; then
    RVAL=`glance add -A $EC2_SECRET_KEY name="$IMAGE_NAME-ramdisk" is_public=true container_format=ari disk_format=ari < "$RAMDISK"`
    RAMDISK_ID=`echo $RVAL | cut -d":" -f2 | tr -d " "`
fi
glance add -A $EC2_SECRET_KEY name="${IMAGE_NAME%.img}" is_public=true container_format=ami disk_format=ami ${KERNEL_ID:+kernel_id=$KERNEL_ID} ${RAMDISK_ID:+ramdisk_id=$RAMDISK_ID} < <(zcat --force "${IMAGE}")


set +o xtrace
