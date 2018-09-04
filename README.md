# Toasts

Toasts is an app that shows desktop notifications from various websites like GitHub,
StackExchange, BitBucket, and the likes. It just runs in the background and shows
you a notification when there is one from sites you have enabled. Authentication to
your user account on a particular website is done through a Personal Access Token or
Oauth.


*Please do note that this project is still a work in progress, even though it works.*


## Supported Sites

- Github

If you would like a new site to be supported, please open an issue, and let's see
what we can do :)

## Getting Started

### Requirements

Toasts is written in Python3 and the package is available on PyPI.

The app has been tested only on Linux, as of now. It should work fine on a Mac, but
Windows is not supportd at the moment (I'm working on it).

### Installation

Open a terminal and:

```shell
$ pip install --user toasts
```

For updating the app:
```shell
$ pip install --user -U toasts
```

### Usage

Before running the app, we should first enable available clients in the
[config file](#the-config-file).
The user config file is `~/.config/toasts/config.yaml` on Linux and
`~/Library/Application Support/toasts/config.yaml` on Mac.

Only Github is implemented for now, so you can enable it in the config file like so:

```yaml
# Config file for toasts

general:
        # List of sites to enable; comma seperated list
        # Default: []
        clients: [github]
        .
        .
        .
```

Toasts gets Github notifications using a Personal Access Token. Create one with
.................................................. permissions. Then set the
environment variables `GH_UNAME` to your Github username and `GH_TOKEN` to the
access token you just created (it is possible to authenticate using your Github
password; just set `GH_TOKEN` to your password). <!-- security - use password as token -->

You're all set !

Open a terminal and and run the `toasts` command:

```shell
$ toasts
```

You should see your notifications pop up, if you have an update from the
enabled sites.

I'm so happy right now :)

## The Config File
 The file is in YAML format:
<!-- add link to yaml site -->

```yaml
# Config file for toasts

general:
        # List of sites to enable; comma seperated list
        # Default: []
        clients: []
        # Connection timeout, in seconds
        # Default: 7 ; Minimum value: 1
        conn_timeout: 7
        # Check for notifications every ___ minutes
        # Default: 3 ; Minimum value: 2
        check_every: 3
        # Show notification for ___ seconds
        # Default: 7 ; Minimum value: 2
        notif_timeout: 7
        # Maximum number of notifications to show at a time, of individual clients.
        # Default: 2
        # Note: Value of -1 will show all notifications; it may clutter your workspace.
        notif_max_show: 2

sites:
        github:
                # *Environment variable* which holds your github username
                # Default: GH_UNAME
                username: GH_UNAME
                # *Environment variable* which holds a personal access token for authentication
                # Default: GH_TOKEN
                token: GH_TOKEN
```

## Known Issues

Unread notifications will be shown again until you mark them as read in the
corresponding website. It's planned to be fixed in the next release.
