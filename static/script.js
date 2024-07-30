function success(msg){
    if (msg=="1"){
        alert("Data added successfully")
    }
    else if(msg=="2"){
        alert("Already Exist")
    }
}

var status="{{msg2}}"
if (status=="1"){
    alert("Not Found")
}

function disableButton() {
    setTimeout(function() {
        alert("Generated");
    }, 100); // 2000 milliseconds = 2 seconds
}

function disableButton1(status) {
        if (status!=1){
            alert("Not Checked")
        }
}

function gen_stop()
{
    alert("Already generated")
}
function mail_stop()
{
    alert("Already sent")
}

function Delete()
{
    var res=confirm("Are you sure you want to proceed?");
    if (res==True){
        return true;
    }
    else{
        return false;
    }
}


