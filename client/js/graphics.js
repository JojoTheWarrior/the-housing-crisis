const CELL_LENGTH = 25;  // sidelength of cell in pixels
const MAP_LENGTH = 25;
const NUM_DISTRICTS = 10;
const PERSPECTIVE_ANGLE = 60;
const OCTAVE = 30;
const WATER_THRESHOLD = 0.35;


const ORIGIN = {
	x: window.innerWidth / 2,
	y: -200
}
const MOUSE = {
	prev_x: 0,
	prev_y: 0,
}
var cells = [];


class Cell {
	constructor(x, y, colour) {
		this.x = x;
		this.y = y;
		this.colour = colour;
		this.sprite = null;

		this.apothem_x = CELL_LENGTH * sqrt(2);
		this.apothem_y = CELL_LENGTH * sin(radians(PERSPECTIVE_ANGLE));
	}

	draw() {
		let x = ORIGIN.x - (this.apothem_x * this.x) + (this.apothem_x * this.y)
		let y = ORIGIN.y + (this.apothem_y * this.x) + (this.apothem_y * this.y)

		fill(...this.colour);
		stroke(...this.colour);
		beginShape();

		vertex(x, y);
		vertex(x - this.apothem_x, y + this.apothem_y);
		vertex(x, y + 2 * this.apothem_y);
		vertex(x + this.apothem_x, y + this.apothem_y);

		endShape(CLOSE);
	}
}


function mousePressed() {
	MOUSE.prev_x = mouseX;
	MOUSE.prev_y = mouseY;
}

function mouseDragged() {
	ORIGIN.x -= MOUSE.prev_x - mouseX;
	ORIGIN.y -= MOUSE.prev_y - mouseY;

	MOUSE.prev_x = mouseX;
	MOUSE.prev_y = mouseY;
}


function perlin(x, y) {
	return noise(x / OCTAVE, (y + 10000) / OCTAVE)
}

function generate_districts() {
	let origin_points = [];
	let colours = [];

	while (origin_points.length < NUM_DISTRICTS) {
		let ox = random(0, MAP_LENGTH);
		let oy = random(0, MAP_LENGTH);

		if (perlin(ox, oy) > WATER_THRESHOLD) {
			origin_points.push([ox, oy]);
			//80, 191, 110
			colours.push([random(22,80), random(130,191), random(51,110)]);
			//colours.push([random(0,255), random(0,255), random(0,255)]);
		}
	}

	for (let x = 0; x <= MAP_LENGTH; x++) {
		for (let y = 0; y <= MAP_LENGTH; y++) {

			if (perlin(x, y) < WATER_THRESHOLD) {
				cells.push(new Cell(x, y, [83, 104, 176]));
				continue;
			}

			let min_distance = Infinity;
			let min_index = -1;

			for (let i = 0; i < origin_points.length; i++) {
				// euclidian
				let distance = dist(x, y, origin_points[i][0], origin_points[i][1]);

				// manhattan
				//let distance = abs(x - origin_points[i][0]) + abs(y - origin_points[i][1]);
				
				if (distance < min_distance) {
					min_distance = distance;
					min_index = i;
				}
			}

			cells.push(new Cell(x, y, colours[min_index]));
		}
	}
}


function setup() {
	console.log("SETUP");
	let canvas = createCanvas(windowWidth, windowHeight);
	canvas.position(0,0);

	background(240,240,240);

	generate_districts();
}


function draw() {
	background(240,240,240);

	for (let cell of cells) {
		cell.draw();
	}
}