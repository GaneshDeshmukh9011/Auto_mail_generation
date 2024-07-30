function showFileName(index) {
    var fileInput = document.getElementById('fileInput' + index);
    var fileNameDisplay = document.getElementById('fileNameDisplay' + index);
    
    if (fileInput.files.length > 0) {
        var fileName = fileInput.files[0].name;
        alert('File chosen: ' + fileName);
        fileNameDisplay.innerHTML = 'Chosen File: ' + fileName;
    }
}

function showReplaceSuccess(index) {
    var fileInput = document.getElementById('fileInput' + index).value;
    if (fileInput === "") {
        alert("Please Choose pdf file");
        return false; // Prevent form submission
    }
}

function show() {
    // Your custom logic for the 'Notify' button click
    // Access form data and make a request to /login
    var form = document.getElementById('myForm');
    var formData = new FormData(form);

    fetch('/login11', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        console.log('Response from /login:', data);
        // Handle the response as needed
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function notify(){
    alert("Already Notify")
}

function submitForm() {
    document.getElementById("myForm").submit();

}

function not_submit(msg1){
    if (msg1){
        alert("Not Generated")
    }
}