# Lost Data Retrieval — Safe Test Environment

This document describes a simulated lost-data recovery exercise using a test disk image.
Perform all actions in an isolated environment (VM or disposable container). Do not attempt to recover data from devices you don't own or have explicit permission for.

## Overview

Goal: simulate accidental file deletion on a FAT32 image and attempt recovery using open-source tools (TestDisk / PhotoRec). Document steps and results.

Files added to this repo:
- `create_test_image.sh` — helper script to build a FAT32 disk image, populate it with sample files, and then delete chosen files to simulate data loss.
- `Lost_Data_Retrieval.md` — this document.

## Requirements

- Linux environment with the following installed: `dd`, `mkfs.vfat` (from `dosfstools`), `mount` (or use `mtools`), and `testdisk` / `photorec`.
- Root or appropriate permissions to mount loop devices if you plan to mount the image.

## Safety note

All commands in this guide operate on a disk image file and not on real physical drives. Always verify the target path before running disk-modifying commands.

## Workflow

1. Create a sparse disk image, format it as FAT32, and add sample files.
2. Delete some files to simulate accidental deletion.
3. Use `testdisk` / `photorec` to scan the image and attempt recovery.
4. Record recovered files and compare with original set.

## Example commands (manual)

Create image (10 MiB FAT32):

```bash
fallocate -l 10M fat32.img
mkfs.vfat fat32.img
```

Mount image (requires root):

```bash
sudo mkdir -p /mnt/fat32img
sudo mount -o loop fat32.img /mnt/fat32img
# create sample files
sudo cp /etc/hosts /mnt/fat32img/hosts.orig
echo "secret password: hunter2" | sudo tee /mnt/fat32img/notes.txt
sudo touch /mnt/fat32img/keep_me.txt
# simulate deletion
sudo rm /mnt/fat32img/notes.txt
sync
sudo umount /mnt/fat32img
```

Scan with TestDisk:

```bash
sudo testdisk fat32.img
# use the interactive menu: analyze -> Quick Search -> list files -> recover
```

Or use PhotoRec to carve files:

```bash
sudo photorec fat32.img
# choose filesystem type [FAT/NTFS], choose options, select free or whole space, run and save recovered files to safe folder
```

## Interpreting results

- `testdisk` may be able to list and undelete directory entries (best for recently deleted files with intact directory records).
- `photorec` recovers file data by carving based on file signatures; filenames and directory structure may be lost.

## What to document after a run

- Command lines used.
- Which files were recovered and their integrity (open/inspect contents).
- Any errors or unexpected behavior.
- Time taken and disk image characteristics.

## Next steps

- Run `create_test_image.sh` in a safe environment to auto-generate the image and deletion scenario.
- If you want, I can add automated checks comparing original and recovered files and produce a short report.

---

Created for Task 3: Lost Data Retrieval (safe simulation and documentation).

## Run results (performed here)

I executed the provided simulation and performed a non-interactive recovery using `sleuthkit` tools. Summary:

- Installed required tools: `dosfstools`, `testdisk` (contains `photorec`), and `sleuthkit`.
- Created image with: `./create_test_image.sh` → produced `fat32.img` (10M).
- Listed filesystem entries (including deleted ones):

```bash
fls -f fat fat32.img
```

Output showed deleted entries for `file1.txt` and `secrets.txt` (identified by metadata ids 4 and 6).

- Recovered files using `icat`:

```bash
icat -f fat fat32.img 4 > recovered_files/file1_recovered.txt
icat -f fat fat32.img 6 > recovered_files/secrets_recovered.txt
```

- Results saved under the repository `recovered_files/`:
	- `file1_recovered.txt` — contains: "This is a sample file."
	- `secrets_recovered.txt` — contains: "password=supersecret"

Notes:
- `sleuthkit`'s `fls`/`icat` approach recovered the original file content and preserved the data despite deletion — this demonstrates how directory metadata and cluster pointers can enable recovery on FAT32 when data blocks remain intact.
- `photorec`/`testdisk` remain available for more interactive or signature-based carving if you prefer those workflows.

If you'd like, I can run an automated comparison between the original files (created during the simulation) and the recovered files, or script a non-interactive `photorec` run via `expect` and record its output.