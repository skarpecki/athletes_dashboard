
window.onload = function() {
    
    const exercisesURL = "http://127.0.0.1:5000/exercises/"
    
    fetch(exercisesURL, { method: "GET", redirect: "follow" }).then(function(response){
        return response.json();
    }).then(function(jsonArray) {
        fillExerciseSelector(jsonArray);
    }).catch(function(err) {
        console.log(err.message);
    });
    
    const exerciseBtn = document.getElementById("add-exercise-btn")  
    if(exerciseBtn !== null) 
    {
        exerciseBtn.onclick = insertExercise;
    } 

    document.getElementById("exercise-name-selector").ondblclick = function() {
        const exerciseArticle = document.getElementsByName("exercise")[0];
        const exerciseForm = document.getElementById("add-exercise-form");
        const radioBtns = document.getElementsByName("type");

        if(typeof exerciseArticle !== "undefined")
        {
            getExerciseJSON(this.value).then(json => 
                exerciseArticle.innerHTML = getExerciseArticleHTML(json));
        }
        else if(typeof exerciseForm !== "undefined")
        {
            getExerciseJSON(this.value).then(json => {
                document.getElementById("exercise-name").value = json["name"];
                document.getElementById("exercise-description").value =  "description" in json ? json["description"] : "";
                document.getElementById("exercise-video").value = "video_url" in json ? json["video_url"] : "https://www.youtube.com/embed/FJRMldSmy-M";
                radioBtns.forEach(btn => {
                    if("type" in json && btn.value.toLowerCase() === json["type"].toLowerCase())
                    {
                        btn.checked = true;
                    }
                });
            });
        }
    }
}

function getExerciseArticleHTML(json) {
    let name = `<h1>${json.name}</h1>`;
    let type = `<h2>${json.type.charAt(0).toUpperCase() + json.type.slice(1).toLowerCase()} exercise</h2>`;
    let description = ``;
    if(("description" in json) == true)
    {
        description = `<h3>Description</h3>
                    <p>${json.description}</p>`;
    }
    let additionalDescription = ``;
    /* if(athlete in addtional description)
     * {
     *   create additional description part  
     * }
     */
    let video_url = ``;
    if(("video_url" in json) == true)
    {
        video_url = `<iframe width="560" height="315" src="${json.video_url}" title="YouTube video player" frameborder="0" allowfullscreen></iframe>`;
    }

    return `${name}
     ${type}
     ${description}
     ${additionalDescription}
     ${video_url}`
}

function getExerciseJSON(exerciseID) {
    let exerciseUrl = `http://127.0.0.1:5000/exercises/${exerciseID}`;
    return fetch(exerciseUrl).then(function(response) {
        return response.json();
    }).then(function(json) {
        return json;
    }).catch(function(err) {
        console.log(err.message);
    })
}

var fillExerciseSelector = jsonArray => {
    const select = document.querySelector("select")
    claerSelectElements(select);
    jsonArray["exercises"].forEach(element => {
        let opt = document.createElement("option");
        opt.value=element._id;
        opt.text=element.name;
        select.appendChild(opt);
})};


var handleExerciseTypeClick = (btn) => {
    let url = `http://127.0.0.1:5000/exercises/?type=${btn.value}`;
    if(btn.value == "all")
    {
        url = `http://127.0.0.1:5000/exercises/`;
    }
    fetch(url).then(function(response){
        return response.json()
    }).then(function(json) {
        fillExerciseSelector(json);
    }).catch(function(err){
        console.log(err.message);
    });
}

var claerSelectElements = selectElement => {
    for(let i = selectElement.options.length - 1; i >= 0; i--)
    {
        selectElement.remove(i);
    }
};

var validateExerciseForm = formData => {
    isValid = true;
    for (let [key, value] of formData.entries()) { 
        if(key=="description" || key=="athletes_descriptions")
        {
            continue;
        }
        if(value=="")
        {
            alert(`Exercise ${key} cannot be empty!`);
            return false;
        }
        if(key=="video_url" && !validateURL(value))
        {
            alert("Provide correct video URL!");
            return false;
        }
    }
    return true;
}

var validateURL = value => {
    let url;
    try 
    {
        url = new URL(value);
    } 
    catch (_) 
    {
        return false;
    }
    return true;
}

var validateExerciseType = (radioBtns) => {
    for(let i = 0; i < radioBtns.length; i++)
    {
        if(radioBtns[i].checked)
        {
            return true;
        }
    }
    alert("Select exercise type!")
    return false;
}

var makeYoutubeEmbed = (url) => {
    var url = url.replace("watch?v=", "embed/");
    return url;
}

function insertExercise() {
    let form = document.getElementById("add-exercise-form");
    let formData = new FormData(form);
    let radioBtns = document.getElementsByName("type");
    if(!validateExerciseForm(formData) || !validateExerciseType(radioBtns))
    {
        return false;
    }
    let object = {};

    for (let [key, value] of formData.entries()) { 
        if(key == "video_url")
        {
            value = makeYoutubeEmbed(value);
        }
        object[key] = value;
    }

    let jsonString = JSON.stringify(object);
    const XHR = new XMLHttpRequest();

    XHR.addEventListener( "load", event => {
        if(XHR.status != 201)
        {
            alert(event.target.responseText);
        }
        else 
        {
            document.getElementById("exercise-name").value = "";
            document.getElementById("exercise-description").value =  "";
            document.getElementById("exercise-video").value = "";
            radioBtns.forEach(btn => btn.checked = false);
        }
    });

    XHR.addEventListener("error", event => {
        alert(event.target.responseText);
    });

    XHR.open( "POST", "http://127.0.0.1:5000/exercises/");       
    XHR.setRequestHeader("Content-Type", "application/json;charset=UTF-8") 
    XHR.send(jsonString);
}