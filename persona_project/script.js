document.getElementById('imageUpload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                processImage(img);
            }
            img.src = event.target.result;
        }
        reader.readAsDataURL(file);
    }
});

function processImage(img) {
    const goodCanvas = document.getElementById('goodPersonaCanvas');
    const evilCanvas = document.getElementById('evilPersonaCanvas');
    const goodCtx = goodCanvas.getContext('2d');
    const evilCtx = evilCanvas.getContext('2d');

    // Resize and draw original image on both canvases
    const size = 256;
    goodCanvas.width = size;
    goodCanvas.height = size;
    evilCanvas.width = size;
    evilCanvas.height = size;

    goodCtx.drawImage(img, 0, 0, size, size);
    evilCtx.drawImage(img, 0, 0, size, size);

    // Apply "good" persona filter (example: brighten)
    applyGoodPersona(goodCtx, size);

    // Apply "evil" persona filter (example: darken and grayscale)
    applyEvilPersona(evilCtx, size);
}

function applyGoodPersona(ctx, size) {
    const imageData = ctx.getImageData(0, 0, size, size);
    const data = imageData.data;
    for (let i = 0; i < data.length; i += 4) {
        // Increase brightness
        data[i] = Math.min(255, data[i] * 1.2);
        data[i+1] = Math.min(255, data[i+1] * 1.2);
        data[i+2] = Math.min(255, data[i+2] * 1.2);
    }
    ctx.putImageData(imageData, 0, 0);
}

function applyEvilPersona(ctx, size) {
    const imageData = ctx.getImageData(0, 0, size, size);
    const data = imageData.data;
    for (let i = 0; i < data.length; i += 4) {
        // Decrease brightness
        data[i] = Math.max(0, data[i] * 0.8);
        data[i+1] = Math.max(0, data[i+1] * 0.8);
        data[i+2] = Math.max(0, data[i+2] * 0.8);

        // Apply grayscale
        const avg = (data[i] + data[i+1] + data[i+2]) / 3;
        data[i] = avg;
        data[i+1] = avg;
        data[i+2] = avg;
    }
    ctx.putImageData(imageData, 0, 0);
}
