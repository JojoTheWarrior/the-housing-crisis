const submissionButton = document.getElementById("submission");
const userPrompt = document.getElementById("textPrompt");
const userPlay = document.getElementById("play");
const userNext = document.getElementById("next");
const userQuestion = document.getElementById("instructions");
const userReplay = document.getElementById("replay");

let approvalValue = 80;
let maxApprovalValue = 100;
let houseCost = 20000; //change as necessary

let city_avg_house_price;
let city_public_support;
let game_state;

var images = [];
var sprites = {};

userPlay.addEventListener("click", function(){
    document.getElementById("landingPage").style.display = "none";
    document.getElementById("infoPage").style.display = "block";
})

userNext.addEventListener("click", function(){
    document.getElementById("infoPage").style.display = "none";
    document.getElementById("gamePage").style.display = "block";
    // loop();
})

userQuestion.addEventListener("click", function(){
    document.getElementById("gamePage").style.display = "none";
    document.getElementById("infoPage").style.display = "block";
    // noLoop();
})

userReplay.addEventListener("click", function(){
	document.getElementById("landingPage").style.display = "flex";
	document.getElementById("gameOverPage").style.display = "none";

})

function changeBar(){
    const ratingBar = document.querySelector('.support');
    const percentage = (approvalValue / maxApprovalValue) * 100;

    ratingBar.style.width = `${percentage}%`;
    ratingBar.innerText = `${Math.ceil(percentage)}%`;

    if (percentage < 25) {
        document.getElementById("gameOverPage").style.display = "block";
        document.getElementById("gamePage").style.display = "none";
    }
}

userPrompt.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        submitPrompt();
    }
});

submissionButton.addEventListener("click", function(e) {
    e.preventDefault();
    submitPrompt();
});

function submitPrompt() {
  // changeBar();
  const promptText = document.getElementById("textPrompt").value;
  document.getElementById("textPrompt").value = '';

  // document.getElementById("cost").innerText = "$"+houseCost;

  //testing
  document.getElementById("submittedPrompt").innerText = promptText;

  showLoading();

  fetch("http://127.0.0.1:5000/send-prompt",
	{
	    headers: {
	      'Accept': 'application/json',
	      'Content-Type': 'application/json',
	      'Access-Control-Allow-Origin': '*'
	    },
	    method: "POST",
	    // mode: 'no-cors',
	    body: JSON.stringify({
    		"prompt": promptText
		})
	})
	.then(function(res){
		let response = res.json()
		response.then((resp) => {
			images = resp.images;
			sprites = resp.sprites;

			console.log(resp);

			for (let cell of cells) {
				cell.sprite = null;
			}

			for (const [sprite, coords] of Object.entries(sprites)) {
				for (let coord of coords) {
					cells[coord[1] + coord[0] * (MAP_LENGTH + 1)].sprite = loadImage("data:image/png;base64," + images[sprite]);
				}
			}

			document.getElementById("cost").innerText = "$" + resp.avg_house_price.toString();
			approvalValue = resp.city_public_support * 100;
			changeBar();
			hideLoading();
		})
	})
	.catch(function(res){
		console.log("Error!")
		console.log(res)
		hideLoading();

	});



  // Simulate a response from the server
  // async () => {
  //   try {
  //       const response = await fetch('/process-prompt', {
  //           method: 'POST',
  //           headers: {
  //               'Content-Type': 'application/json',
  //           },
  //           body: JSON.stringify({ input_string: promptText }),
  //       });
        
  //       const data = await response.json();

  //       city_avg_house_price = data[0];
  //       city_public_support = data[1];
  //       game_state = data[2];
  //       images = data[3];

  //       console.log("Received Array:", data);
  //   } catch (error) {
  //       console.error("Error:", error);
  //   }
  // }

}

function showLoading() {
    document.getElementById("gamePage").style.display = "none";
    document.getElementById("landingPage").style.display = "none";
    document.getElementById("infoPage").style.display = "none";
    document.getElementById("loadingPage").style.display = "flex";
}    

function hideLoading() {
    document.getElementById("loadingPage").style.display = "none";
    document.getElementById("gamePage").style.display = "block";

	if ((approvalValue / maxApprovalValue) * 100 < 30){
		document.getElementById("gamePage").style.display = "none";
		document.getElementById("gameOverPage").style.display = "flex";
	}
}

// test loading
const loadScreen = document.getElementById("loadingScreen");
let isLoading = false;

loadScreen.addEventListener("click", function () {
    if (isLoading) {
        hideLoading();
    } else {
        showLoading();
    }
    isLoading = !isLoading;
});

// graphics.js begins
const CELL_LENGTH = 25;  // sidelength of cell in pixels
const MAP_LENGTH = 10;
const NUM_DISTRICTS = 6;
const PERSPECTIVE_ANGLE = 60;
const OCTAVE = 25;
const WATER_THRESHOLD = 0.0;
const CELL_DEPTH = 40;
const PERLIN_AMPLIFICATION = 70;


const ORIGIN = {
	x: window.innerWidth / 2,
	y: 130
}
const MOUSE = {
	prev_x: 0,
	prev_y: 0,
}
var cells = [];
var district_cells = {};
const APOTHEM_X = CELL_LENGTH * Math.sqrt(2);
const APOTHEM_Y = CELL_LENGTH * Math.sin(PERSPECTIVE_ANGLE * Math.PI / 180);

var fade_out = 0;

class Cell {
	constructor(x, y, z_offset, district, colour) {
		this.x = x;
		this.y = y;
		this.z_offset = 0;
		this.is_hovered = false;
		this.peaked = false;
		this.animation = district * 700;
		this.district = district;
		this.colour = colour;
		this.sprite = null;
	}

	draw() {
		this.z_offset = 7 * Math.sin(2 * ((Date.now() - this.animation) / 1000));
		if (this.district <= 0)
			this.z_offset -= 15;

		if (this.is_hovered) {
			this.z_offset = 7 * Math.sin(2 * ((Date.now() - this.animation) / 1000));
			if (Math.sin(2 * ((Date.now() - this.animation) / 1000)) >= 0.95)
				this.peaked = true;
		}

		if (this.peaked)
			this.z_offset = 14;

		let x = ORIGIN.x - (APOTHEM_X * this.x) + (APOTHEM_X * this.y)
		let y = ORIGIN.y + (APOTHEM_Y * this.x) + (APOTHEM_Y * this.y) - this.z_offset;
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

	check_hover() {
		if (this.district <= 0)
			return -1;

		let x = ORIGIN.x - (APOTHEM_X * this.x) + (APOTHEM_X * this.y)
		let y = ORIGIN.y + (APOTHEM_Y * this.x) + (APOTHEM_Y * this.y) - this.z_offset
		if (point_in_rhombus(mouseX, mouseY, x, y, APOTHEM_X, APOTHEM_Y))
			return this.district
		return -1
	}
}


function point_in_rhombus(x, y, ax, ay, verticalDist, horizontalDist) {
    // Center coordinates
    let cx = ax;
    let cy = ay + verticalDist;

    // Compute dx and dy from center
    let dx = Math.abs(x - cx) - 5;
    let dy = Math.abs(y - cy) - 5;

    // Check if point is within rhombus using Manhattan-style condition
    return (dx / horizontalDist + dy / verticalDist) <= 1;
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
	year_passes();
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
			if (min_index + 1 == 0)
				continue;

			let new_cell = new Cell(
				x,
				y,
				(perlin(origin_points[min_index][0], origin_points[min_index][1])) * PERLIN_AMPLIFICATION,
				min_index + 1,
				colours[min_index]
			);
			cells.push(new_cell);
			if (Object.keys(district_cells).includes((min_index + 1).toString()))
				district_cells[min_index + 1].push(new_cell);
			else
				district_cells[min_index + 1] = [new_cell];
		}
	}
}

function year_passes() {
	fade_out = 255;
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
	      'Access-Control-Allow-Origin': '*'
	    },
	    method: "POST",
	    //mode: 'no-cors',
	    body: JSON.stringify(send_data)
	})
	.then(function(res){
		let response = res.json()
		response.then((resp) => {
			console.log(resp);
			images = resp.images;
			sprites = resp.sprites;

			for (const [sprite, coords] of Object.entries(sprites)) {
				for (let coord of coords) {
					cells[coord[1] + coord[0] * (MAP_LENGTH + 1)].sprite = loadImage("data:image/png;base64," + images[sprite]);
				}
			}

			document.getElementById("cost").innerText = "$" + resp.avg_house_price.toString();
			approvalValue = resp.city_public_support * 100;
			changeBar();
			//hideLoading();
		})
	})
	.catch(function(res){ console.log(res) });
}

function setup() {
	console.log("SETUP");
    const container = document.getElementById('p5CanvasContainer');
    
	let canvas = createCanvas(windowWidth, windowHeight);
	canvas.parent(container);

	background(240,240,240);

	generate_districts();
	send_district_coords();

	// images["temple"] = loadImage('../../temple.png');
	//cells[47].sprite = loadImage('../../temple.png');
}

    
function draw() {
	background(240,240,240);

	let district = -1;
	for (let cell of cells) {
		cell.draw();
		let d = cell.check_hover();
		if (d !== -1)
			district = d;
	}

	if (district !== -1) {
		noStroke();
		fill(0,0,0);
		text('District ' + district.toString(), mouseX - 20, mouseY - 5);
	}


	// if (!checked) {
	// 	for (let cell of cells) {
	// 		cell.is_hovered = false;
	// 		cell.peaked = false;
	// 	}
	// }

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

    // does fade out
	// noStroke();
	// fill(0, 0, 0, fade_out);
	// rect(0, 0, width, height)
	// fade_out = max(fade_out-5, 0);
}