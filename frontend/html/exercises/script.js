
window.onload = function() {
    
    const exercisesURL = "http://127.0.0.1:5000/exercises/"
    
    fetch(exercisesURL, { method: "GET", redirect: "follow" }).then(function(response){
        return response.json();
    }).then(function(jsonArray) {
        fillExerciseSelector(jsonArray);
    }).catch(function(err) {
        console.log(err.message);
    });
    
    document.getElementById("exercise-name-selector").ondblclick = function() {
        const exerciseArticle = document.getElementsByName("exercise")[0];
        console.log(exerciseArticle);
        // getExerciseJSON(this.value).then(function(json){
        //     exerciseArticle.innerHTML = getExerciseArticleHTML(json);
        // }); 
        getExerciseJSON(this.value).then(json => 
            exerciseArticle.innerHTML = getExerciseArticleHTML(json));
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
    for(var i = selectElement.options.length - 1; i >= 0; i--)
    {
        selectElement.remove(i);
    }
};