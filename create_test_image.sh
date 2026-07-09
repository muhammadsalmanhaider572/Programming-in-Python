#!/usr/bin/env bash

# create_test_image.sh
# Creates a FAT32 disk image, mounts it, populates sample files, then deletes some files
# Run in a safe test environment. Requires root for mounting loopback files.

set -euo pipefail

IMAGE_NAME="fat32.img"
IMAGE_SIZE="10M"
MOUNT_DIR="/mnt/fat32img"
RECOVERY_DIR="recovered_files"

echo "Creating ${IMAGE_NAME} (${IMAGE_SIZE})..."
if ! command -v mkfs.vfat >/dev/null 2>&1; then
  echo "mkfs.vfat not found. Install dosfstools." >&2
  exit 1
fi

fallocate -l ${IMAGE_SIZE} "${IMAGE_NAME}"
mkfs.vfat "${IMAGE_NAME}"

sudo mkdir -p "${MOUNT_DIR}"
sudo mount -o loop "${IMAGE_NAME}" "${MOUNT_DIR}"

# Populate with sample files
echo "This is a sample file." | sudo tee "${MOUNT_DIR}/file1.txt" >/dev/null
echo "password=supersecret" | sudo tee "${MOUNT_DIR}/secrets.txt" >/dev/null
sudo dd if=/dev/urandom bs=1024 count=8 of="${MOUNT_DIR}/random.bin" >/dev/null 2>&1 || true
sudo touch "${MOUNT_DIR}/keep_me.txt"

sync

# Simulate accidental deletion
sudo rm -f "${MOUNT_DIR}/secrets.txt"
sudo rm -f "${MOUNT_DIR}/file1.txt"

sync
sudo umount "${MOUNT_DIR}"

echo "Image ready: ${IMAGE_NAME}" 

echo "When ready, run the following to attempt recovery with testdisk or photorec:"
echo "sudo testdisk ${IMAGE_NAME}"
echo "sudo photorec ${IMAGE_NAME}"

echo "Recovered files should be saved to a directory outside the image, e.g. ${RECOVERY_DIR}."
