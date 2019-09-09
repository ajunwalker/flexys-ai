window.onload = function () {

    var dropzone=document.getElementById('dropzone');

    dropzone.ondrop=function(e){
      fileinput.files=e.dataTransfer.files
      e.preventDefault();
      this.className='dropzone';

      x=e.dataTransfer.files
      console.log(x)
    };

    dropzone.ondragover=function(){
      this.className='dropzone dragover';
      return false;
    };

    dropzone.ondragleave=function(){
     this.className='dropzone';

     return false;
     };
}
