# haptgp

rsync commands:

- sync host to pi: `rsync -rlptzv --progress --delete --exclude=.git --filter='dir-merge,-n /.gitignore' . "admin@haptgp-f.local:/home/admin/projects/haptgp"`
- sync pi to host: `rsync -rlptzv --progress --delete --exclude=.git --filter='dir-merge,-n /.gitignore' "admin@haptgp-f.local:/home/admin/projects/haptgp" .`
