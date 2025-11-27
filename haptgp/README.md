# haptgp

## Using this project

This project uses [uv](https://docs.astral.sh/uv/). It shouldnt be required, but if you don't use it, your mileage may vary. It also expects you to have `rsync` installed on your machine to syncrhonize the code on the pi without leaving your git credentials on it.

## workflow commands

- `uv run scripts/sync.py` (`rsync -rlptzv --progress --delete --exclude=.git --filter='dir-merge,-n /.gitignore' . "admin@haptgp-f.local:/home/admin/projects/haptgp"`)
- `uv run scripts/sync.py --pi` (`rsync -rlptzv --progress --delete --exclude=.git --filter='dir-merge,-n /.gitignore' "admin@haptgp-f.local:/home/admin/projects/haptgp" .`)
