# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "watchdog",
# ]
# ///

from argparse import ArgumentParser
import subprocess


parser = ArgumentParser("sync", "syncs the pi's filesystem with the host's")
modifiers = parser.add_mutually_exclusive_group()
modifiers.add_argument(
    "--host", help="syncs the host with the pi instead", action="store_true"
)
modifiers.add_argument(
    "-w",
    "--watch",
    help="watch the current directory for changes and syncs automatically.",
    action="store_true",
)
parser.add_argument(
    "-u", "--username", default="admin"
)  # TODO: store these in .env instead
parser.add_argument("-p", "--password", default="admin")
parser.add_argument("-n", "--hostname", default="haptgp-f.local")
parser.add_argument("-d", "--directory", default="/home/admin/projects/haptgp")
args = parser.parse_args()

command = [
    "rsync",
    "-rlptzv",
    "--progress",
    "--delete",
    "--exclude=.git",
    "--filter='dir-merge,-n /.gitignore'",
]
pi_connection_str = f'"{args.username}@{args.hostname}:{args.directory}"'

if args.host:
    command.extend([pi_connection_str, "."])
else:
    command.extend([".", pi_connection_str])


def run():
    subprocess.run(command, capture_output=True, stdin=args.password)


if args.watch:
    from watchdog.observers import Observer # type: ignore
    from watchdog.events import FileSystemEventHandler # type: ignore
    from threading import Timer

    class DebouncedDispatchHandler(FileSystemEventHandler):
        def __init__(self, timeout, func):
            self.timeout = timeout
            self.func = func
            self.reset_timer()
            
        def reset_timer(self):
            try:
                self.timer.cancel()
            except AttributeError:
                pass  # the timer is not defined yet
            self.timer = Timer(interval=self.timeout, function=self.func)
            self.timer.start()

        def on_any_event(self, event):
            super().on_any_event(event)
            self.reset_timer()

    observer = Observer()
    observer.schedule(
        DebouncedDispatchHandler(timeout=1, func=run), 
        ".", 
        recursive=True
    )
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
else:
    run()


# https://gist.github.com/walkermatt/2871026
def debounce(wait):
    """Decorator that will postpone a functions
    execution until after wait seconds
    have elapsed since the last time it was invoked."""
    from threading import Timer

    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)

            try:
                debounced.t.cancel()
            except AttributeError:
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()

        return debounced

    return decorator
