let grid = [];
let eraser = false;
let selected = "█";
let selectedElement = "wall";
let tileImages = {};

const tiles = [
    {
        "object": "█",
        "image": "/wall.png",
    },
    {
        "object": "▒",
        "image": "/box.png",
    },
    {
        "object": "x",
        "image": "/end.png",
    },
    {
        "object": "P",
        "image": "/player.png",
    }
]

function preload() {
    for (let index = 0; index < tiles.length; index++) {
        const { object, image } = tiles[index];

        tileImages[object] = loadImage(`./img/tiles${image}`);
    }
}

function setup() {
    const canvas = createCanvas(912, 240);
    canvas.parent("editor");

    grid = Array.from({ length: 5 }, () => Array(19).fill(" "));
}

function draw() {
    background(0, 0, 0);

    noStroke();
    noSmooth();

    const tileSize = 48;
    for (let i = 0; i < grid.length; i++) {
        for (let j = 0; j < grid[i].length; j++) {
            const tileX = j * tileSize;
            const tileY = i * tileSize;
            const tileValue = grid[i][j];

            if (tileImages[tileValue]) image(tileImages[tileValue], tileX, tileY, tileSize, tileSize);
        }
    }

    const gx = int((mouseX - mouseX % 48) / 48);
    const gy = int((mouseY - mouseY % 48) / 48);

    if (mouseIsPressed) {
        const row = floor(mouseY / (height / grid.length));
        const col = floor(mouseX / (width / grid[0].length));

        if (isValidCell(row, col)) grid[row][col] = eraser ? " " : selected;
    }

    fill(eraser ? 255 : 150, eraser ? 255 : 150, eraser ? 255 : 150, 100);
    rect(gx * 48, gy * 48, 48, 48);
}

function isValidCell(row, col) {
    return row >= 0 && row < grid.length && col >= 0 && col < grid[row].length;
}

function setObject(value, id) {
    selected = value;

    document.getElementById(selectedElement).classList.remove("selected");

    selectedElement = id;

    document.getElementById(selectedElement).classList.add("selected");
}

function toggleEraser() {
    eraser ? document.getElementById("eraser").classList.remove("selected") : document.getElementById("eraser").classList.add("selected");

    eraser = !eraser;
}

function resize() {
    const width = Number(window.prompt("What width do you want?"));
    const height = Number(window.prompt("What width do you want?"));

    if (!width || !height) return window.alert("You must set a number for both.")

    if (width > 25 || height > 10) return window.alert("The size cant be more then 25x10.");

    grid = Array.from({ length: width }, () => Array(height).fill(" "));

    resizeCanvas(width * 48 || 912, height * 48 || 240, true);
}

function decodeString(str) {
    let bytes = [];

    for (let i = 0; i < str.length; i++) {
        bytes.push(str.charCodeAt(i));
    }

    return new TextDecoder("utf-8").decode(new Uint8Array(bytes));
}

function decodeArray(data) {
    return data.map(array => array.map(str => decodeString(str)));
}

async function importRoom() {
    try {
        const clipboard = await navigator.clipboard.readText();

        processData(clipboard);
    } catch(err) {
        const level = window.prompt("Please enter the data:");

        processData(level);
    }
}

function processData(clipboardData) {
    grid = decodeArray(JSON.parse(atob(clipboardData)));

    console.log("Data imported successfully.");
}

function exportRoom() {
    const output = btoa(unescape(encodeURIComponent(JSON.stringify(grid))));

    try {
        navigator.clipboard.writeText(output);
    } catch(err) {
        window.alert(output);
    }
}

document.addEventListener("keydown", (event) => event.code === "KeyE" ? toggleEraser() : null);
