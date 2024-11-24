# osu! Metronome

osu! Metronome is a tool designed to help osu! players by adding a metronome beat synced to the map.
It supports osu!stable

## How to use
- Go to [Releases](https://github.com/nekiak/osu-metronome/releases/)
- Download the latest zip file, extract it and run `OsuMetronome.exe`

## Usage
1. **Start osu! and osu!Metronome **: Ensure that both are running
2. **Load a Map**: Open the map you want to modify in the editor
3. **Adjust Metronome Gain**: Use the slider to set the metronome volume.
4. **Apply Metronome**: Click `Apply Metronome` to overlay the metronome ticks onto the map's audio.
5. **Restore Backup**: Click `Restore Backup` if you need to revert to the original audio.


## Troubleshooting
### Access is denied / similar error
- Try playing a different map for a few seconds, then go back to the map you want to modify

### Program does not open
- It might be getting false-flagged by your antivirus due to [a library it uses](https://github.com/pyinstaller/pyinstaller/issues/6754), you should [try making an exception for it](https://support.microsoft.com/en-us/windows/add-an-exclusion-to-windows-security-811816c0-4dfd-af4a-47e4-c301afe13b26)


## Contributing
Contributions are welcome! Here's how you can contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request.
<details>
  <summary></summary>
   trigger warning: shitcode
</details>


## License
This project is licensed under the [MIT License](LICENSE).


## Acknowledgments
- [Tosu](https://github.com/tosuapp/tosu) for providing their API
