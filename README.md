# FrontMan

Tool to help manage frontend dependencies (javascript, css)

Inspired by dotnet LibMan

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
frontman
```

You should see an output like this:

```
OK  https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js -> frontman/assets/jquery/jquery.min.js
OK  https://cdn.jsdelivr.net/npm/@popperjs/core@2.6.0/dist/umd/popper.min.js -> assets/popper/popper.js
OK  https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js -> assets/bootstrap/js/bootstrap.min.js
OK  https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css -> assets/bootstrap/css/bootstrap.min.css
```