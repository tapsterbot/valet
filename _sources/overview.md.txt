<style>
  div.mermaid {
    background: #ffffff;
    width: 100%;
    height: 100%;
  }
</style>
# Architecture Overview

Here's a sequence diagram showing the important parts and how they talk to each other:

```{mermaid}
sequenceDiagram
  %%box rgb(245, 245, 245)
  participant C as Client Automation Script
  %%end
  box rgb(245, 245, 245) Tapster Valet
  participant DS as Display Server
  participant TFT as TFT Display
  participant S as Checkbox Server
  participant CM as Camera / Video Capture
  end
  participant 📱 as Smartphone

  C->>DS: Show text "Running a Demo"
  DS->>TFT: Show text "Running a Demo"
  DS-->>C: OK!
  C->>S: Take snapshot
  S->>CM: Take snapshot
  CM-->>S: Image bytes (binary)
  S-->>C: Image bytes (.png)
  C->>C: Look for text (Tesseract)
  C->>C: Look for a button (OpenCV)
  C->>S: Move pointer to (x=100, y=100)
  S->>📱: Move pointer to (x=100, y=100)
  S-->>C: OK!
  C->>S: Send keys "Hello, World!"
  S->>📱: Send keys "Hello, World!"
  S-->>C: OK!
  C->>DS: Show text "Done ✅"
  DS->>TFT: Show text "Done ✅"
  DS-->>C: OK!
```

<script>
  var drawing = document.getElementsByClassName('mermaid')[0]

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      drawing.requestFullscreen()
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
  }

  drawing.addEventListener('click', toggleFullscreen)
</script>