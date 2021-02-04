# FrontMan - Frontend Library Manager

Tool to help manage frontend dependencies (javascript, css)

Inspired by [AspNet Library Manager](https://github.com/aspnet/LibraryManager)

## Installation

```sh
pip install frontman
```

## Usage

1. Create the manifest file `frontman.json`

```json
{
  "provider": "jsdelivr",
  "destination": "assets",
  "packages": [
    {
      "name": "jquery",
      "version": "3.5.1",
      "provider": "cdnjs",
      "files": [
        {
          "name": "jquery.min.js",
          "destination": "jquery"
        }
      ]
    },
    {
      "name": "@popperjs/core",
      "version": "2.6.0",
      "path": "dist/umd",
      "destination":"popper",
      "files": [
        {
          "name": "popper.min.js",
          "rename": "popper.js"
        }
      ]
    },
    {
      "name": "bootstrap",
      "version": "4.6.0",
      "path": "dist",
      "destination": "bootstrap",
      "files": [
        "js/bootstrap.min.js",
        "css/bootstrap.min.css"
      ]
    }
  ]
}
```

2. Execute FrontMan

```shell
frontman install
```

You should see an output like this:

```
OK   https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js -> assets/jquery/jquery.min.js
OK   https://cdn.jsdelivr.net/npm/@popperjs/core@2.6.0/dist/umd/popper.min.js -> assets/popper/popper.js
OK   https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js -> assets/bootstrap/js/bootstrap.min.js
OK   https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css -> assets/bootstrap/css/bootstrap.min.css
```

## Forcing package download

By default, files that already have been downloaded will be skipped. To force download these files, use the `--force` (or `-f`) flag:

```sh
frontman install --force
```

## Manifest Format

**provider**: The server we will download the files from. It can be `cdnjs`, `jsdelivr` or `unpkg`.

**destination**: Directory where the files will be downloaded.

**packages**: List of packaged to be downloaded.

Each package item have the following format:

**name**: Name of the package, according to the chosen provider.

**version**: Version of the package.

**path** (Optional): The provider may serve the files in a sub path (eg. "dist"). Setting this option will strip the path from the downloaded file path.

**destination** (Optional): Directory inside the top level `destination` where the files from this package will be downloaded.

**provider** (Optional): Provider to use for this package.

**files**: List of files to download for this package.

The files can be specified as string containing the path to the file. The path specified here will be present in the final destination (eg. "js/bootstrap.min.js" will be downloaded to "{destination}/js/bootstrap.min.js")

Files can also be specified as objects with the following format:

**name**: Name of the file to download.

**destination**: Directory to be appended to the previous `destination`.

**rename**: Change the name of the downloaded file.
