

var canvas=document.getElementById("canvas");
var ctx=canvas.getContext("2d");
var lastX;
var lastY;
var mouseX;
var mouseY;
var canvasOffset=$("#canvas").offset();
var offsetX=canvasOffset.left;
var offsetY=canvasOffset.top;
var isMouseDown=false;
var bgcolor = "#000";
var pencolor = "#fff";
var schema = "dark";
var mode="pen";
initialize();

function initialize() {

        $("#pen").find('.glyphicon').css("color", "grey");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        ctx.lineJoin = "round";
        ctx.lineWidth = 3;
        ctx.strokeStyle = pencolor
        ctx.fillStyle= bgcolor;
        ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      }


function handleMouseDown(e){
  mouseX=parseInt(e.clientX-offsetX);
  mouseY=parseInt(e.clientY-offsetY);

  // Put your mousedown stuff here
  lastX=mouseX;
  lastY=mouseY;
  isMouseDown=true;
}

function handleMouseUp(e){
  mouseX=parseInt(e.clientX-offsetX);
  mouseY=parseInt(e.clientY-offsetY);

  // Put your mouseup stuff here
  isMouseDown=false;
}

function handleMouseOut(e){
  mouseX=parseInt(e.clientX-offsetX);
  mouseY=parseInt(e.clientY-offsetY);

  // Put your mouseOut stuff here
  isMouseDown=false;
}

function handleMouseMove(e){
  mouseX=parseInt(e.clientX-offsetX);
  mouseY=parseInt(e.clientY-offsetY);

  // Put your mousemove stuff here
  if(isMouseDown){
    ctx.beginPath();
    if(mode=="pen"){
      ctx.globalCompositeOperation="source-over";
      ctx.moveTo(lastX,lastY);
      ctx.lineTo(mouseX,mouseY);
      ctx.stroke();     
    }else{
      
      ctx.fillStyle= bgcolor;
      ctx.arc(lastX,lastY,60,0,Math.PI*5,false);
      ctx.fill();
    }
    lastX=mouseX;
    lastY=mouseY;
  }
}

function saveViaAJAX()
{
	var testCanvas = document.getElementById("canvas");
	var canvasData = testCanvas.toDataURL("image/png");
	var postData = "canvasData="+canvasData;
	

	//alert("canvasData ="+canvasData );
	var ajax = new XMLHttpRequest();
	ajax.open("POST",'test_save.php',true);
	ajax.setRequestHeader('Content-Type', 'canvas/upload');
	//ajax.setRequestHeader('Content-TypeLength', postData.length);

	ajax.send(postData);
}


document.getElementById('download').addEventListener('click', download, false);
      
      function download() {
    
          var img = canvas.toDataURL('image/png');
          this.href = img; //this may not work in the future..
          
          saveViaAJAX()

        };

$("#color_schema").click(function(){
  
  var r=confirm("Wechsel des Farbschemas löscht den aktuellen Canvas! Fortfahren?");

  if (r==true){
    if (schema == "dark"){
  
      bgcolor="#fff";
      pencolor="#000"; 
      schema = "white";
    }
    else{

      bgcolor="#000";
      pencolor="#fff";
      schema = "dark";
    }

    initialize();
  }

});

$("#clear").click(function(){
  
  var r=confirm("Canvas löschen?");
  
  if (r == true){
  
    ctx.fillStyle= bgcolor; ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  
  }

});
$("#canvas").mousedown(function(e){handleMouseDown(e);});
$("#canvas").mousemove(function(e){handleMouseMove(e);});
$("#canvas").mouseup(function(e){handleMouseUp(e);});
$("#canvas").mouseout(function(e){handleMouseOut(e);});


$("#pen").click(function(){ 
  
  if (mode != "pen"){
  
    $('.glyphicon').css("color", "#000000");  
    $(this).find('.glyphicon').css("color", "grey");
    mode="pen";
  }

});

$("#eraser").click(function(){ 

  if (mode != "eraser"){
  
    $('.glyphicon').css("color", "#000000"); 
    $(this).find('.glyphicon').css("color", "grey");
    mode="eraser";
  }

});