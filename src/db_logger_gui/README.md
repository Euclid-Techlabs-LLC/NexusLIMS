# DB Logger GUI

## Dependencies

See `requirements.txt`.

## Run interactively

1. Edit config file -- `$HOME/.nexuslims/gui/config.json`
2. `python main.py`

## Packaging as single executable

Require `pyinstaller` installed. (`pip install pyinstaller`)

### On Windows PowerShell
```powershell
pyinstaller -y -F -w `
    -n "NexusLIMS Session Logger" `
    -i "resources\\logo_bare_xp.ico" `
    --add-data "resources;resources" main.py
```

### On MacOS
```bash
pyinstaller -y -F -w \
    -n "NexusLIMS Session Logger" \
    -i "resources/logo_bare_xp.ico" \
    --add-data "resources:resources" main.py
```