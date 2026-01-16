# Quick Card Video

Generate a static image and 10-second video from a text prompt.

## Usage

```bash
python app.py "Your sentence here"
```

Optional config in `config.yaml`:
- `font_size`
- `font_color`
- `background_color`

## Change Log

### Unreleased
- Add base image + video renderer.
- Configure light background and readable font color defaults.
- Remove text shadow for pure text rendering.
- Add `.gitignore` with Python defaults and `outputs/` ignored.
