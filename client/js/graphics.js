const CELL_LENGTH = 25;  // sidelength of cell in pixels
const MAP_LENGTH = 10;
const NUM_DISTRICTS = 4;
const PERSPECTIVE_ANGLE = 60;
const OCTAVE = 25;
const WATER_THRESHOLD = 0.35;
const CELL_DEPTH = 40;
const PERLIN_AMPLIFICATION = 70;


const ORIGIN = {
	x: window.innerWidth / 2,
	y: 100
}
const MOUSE = {
	prev_x: 0,
	prev_y: 0,
}
var cells = [];
const APOTHEM_X = CELL_LENGTH * Math.sqrt(2);
const APOTHEM_Y = CELL_LENGTH * Math.sin(PERSPECTIVE_ANGLE * Math.PI / 180);

var images = [];


class Cell {
	constructor(x, y, z_offset, district, colour) {
		this.x = x;
		this.y = y;
		this.z_offset = z_offset;
		this.district = district;
		this.colour = colour;
		this.sprite = null;
	}

	draw() {
		let x = ORIGIN.x - (APOTHEM_X * this.x) + (APOTHEM_X * this.y)
		let y = ORIGIN.y + (APOTHEM_Y * this.x) + (APOTHEM_Y * this.y) - this.z_offset
		let depth = CELL_DEPTH;
		if (this.x == MAP_LENGTH || this.y == MAP_LENGTH)
			depth = CELL_LENGTH * 2;

		// TOP

		fill(...this.colour);
		stroke(...this.colour);
		beginShape();

		vertex(x, y);
		vertex(x - APOTHEM_X, y + APOTHEM_Y);
		vertex(x, y + 2 * APOTHEM_Y);
		vertex(x + APOTHEM_X, y + APOTHEM_Y);

		endShape(CLOSE);

		// LEFT

		fill(...highlight(this.colour, 10));
		//stroke(...highlight(this.colour, 10));
		noStroke();

		beginShape();

		vertex(x - APOTHEM_X, y + APOTHEM_Y);
		vertex(x - APOTHEM_X, y + APOTHEM_Y + depth);
		vertex(x, y + 2 * APOTHEM_Y + depth);
		vertex(x, y + 2 * APOTHEM_Y);

		endShape(CLOSE);

		// RIGHT

		fill(...highlight(this.colour, -10));
		//stroke(...highlight(this.colour, -10));
		noStroke();

		beginShape();

		vertex(x, y + 2 * APOTHEM_Y);
		vertex(x, y + 2 * APOTHEM_Y + depth);
		vertex(x + APOTHEM_X, y + APOTHEM_Y + depth);
		vertex(x + APOTHEM_X, y + APOTHEM_Y);

		endShape(CLOSE);

		this.draw_image(x, y);
	}

	draw_image(x, y) {
		if (this.sprite !== null) {
			this.sprite.resize(APOTHEM_X * 2, 0);
			image(this.sprite, x - APOTHEM_X, y - 20);
		}
	}
}


function highlight(colour, factor) {
	let return_colour = [];

	for (let i of colour) {
		let i2 = i + factor;

		if (i2 > 255)
			i2 = 255;
		else if (i2 < 0)
			i2 = 0;

		return_colour.push(i2);
	}

	return return_colour;
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
				cells.push(new Cell(x, y, (WATER_THRESHOLD * PERLIN_AMPLIFICATION) - 5, -1, [83, 104, 176]));
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
			//console.log(perlin(origin_points[min_index][, origin_points[min_index]));
			cells.push(new Cell(
				x,
				y,
				(perlin(origin_points[min_index][0], origin_points[min_index][1])) * PERLIN_AMPLIFICATION,
				min_index + 1,
				colours[min_index]
			));
		}
	}
}

function send_district_coords() {
	let send_data = {};


	for (let cell of cells) {

		if (Object.keys(send_data).includes(cell.district.toString())) {
			send_data[cell.district].push([cell.x, cell.y]);
		}
		else {
			send_data[cell.district] = [[cell.x, cell.y]];
		}
	}

	console.log(send_data);

	fetch("http://127.0.0.1:5000/send-district-coords",
	{
	    headers: {
	      'Accept': 'application/json',
	      'Content-Type': 'application/json',
	    },
	    method: "POST",
	    mode: 'no-cors',
	    body: JSON.stringify(send_data)
	})
	.then(function(res){ console.log(res) })
	.catch(function(res){ console.log(res) });
}


function setup() {
	console.log("SETUP");
	let canvas = createCanvas(windowWidth, windowHeight);
	canvas.position(0,0);

	background(240,240,240);

	generate_districts();
	send_district_coords();

	//images.push(loadImage('data:image/png;base64,PCFkb2N0eXBlIGh0bWw+CjxodG1sIGxhbmc9ZW4+Cjx0aXRsZT40MTUgVW5zdXBwb3J0ZWQgTWVkaWEgVHlwZTwvdGl0bGU+CjxoMT5VbnN1cHBvcnRlZCBNZWRpYSBUeXBlPC9oMT4KPHA+RGlkIG5vdCBhdHRlbXB0IHRvIGxvYWQgSlNPTiBkYXRhIGJlY2F1c2UgdGhlIHJlcXVlc3QgQ29udGVudC1UeXBlIHdhcyBub3QgJiMzOTthcHBsaWNhdGlvbi9qc29uJiMzOTsuPC9wPgo='));
	//cells[0].sprite = images[0];
	//cells[0].sprite.resize(50,0);
}


function draw() {
	background(240,240,240);

	for (let cell of cells) {
		cell.draw();
	}

	// noStroke();
	// fillGradient('linear', {
	//     from : [ORIGIN.x, ORIGIN.y],   // x, y : Coordinates
	//     to : [ORIGIN.x - (MAP_LENGTH * APOTHEM_X), ORIGIN.y + (2 * MAP_LENGTH * APOTHEM_Y)], // x, y : Coordinates
	//     steps : [
	//         color(240,240,240,0),
	//         color(240,240,240,0),
	//         color(240)
	//     ] // Array of p5.color objects or arrays containing [p5.color Object, Color Stop (0 to 1)]
	// });
}