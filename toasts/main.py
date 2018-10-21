import sys

from .app import ToastsApp


def main():
    print("Press Control-C to quit")
    try:
        ToastsApp().run()
    except KeyboardInterrupt:
        sys.exit(0)
