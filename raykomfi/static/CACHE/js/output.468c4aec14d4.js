(function($){$("#lazyLoadLink").on("click",function(){var link=$(this);var page=link.data("page");$.ajax({type:"post",url:"/api/lazy-posts/",data:{page:page,csrfmiddlewaretoken:Cookies.get("csrftoken"),},success:function(data){if(data.has_next){link.data("page",page+1);}else{link.hide();}
$("#raykomfi-posts").append(data.posts_html);},error:function(xhr,status,error){console.log(error);},});});$("#lazyLoadLinkComments").on("click",function(){var link=$(this);var page=link.data("page");$.ajax({type:"post",url:"/api/lazy-comments/",data:{page:page,post_id:parseInt(document.getElementById("post_id").value),csrfmiddlewaretoken:Cookies.get("csrftoken"),},success:function(data){if(data.has_next){link.data("page",page+1);}else{link.hide();}
$("#posts-wrapper").append(data.comments_html);},error:function(xhr,status,error){console.log(error);},});});})(jQuery);;function addReply(e){e.preventDefault();console.log(e);}
let post_wrapper=$("#posts-wrapper");let message_view=$("#messages-view");let view_html="";$(document).on("submit","form.replyForm",function(e){e.preventDefault();let content=e.target[0].value;let{commentId}=e.target.dataset;if(content){axios({method:"POST",url:"/api/reply/add",headers:{"X-CSRFTOKEN":Cookies.get("csrftoken"),"Content-Type":"application/json",},data:{content:content,comment_id:parseInt(commentId),},}).then((response)=>{let comment_view=$(`#comment-id-${commentId}`);view_html=response.data.view;console.log(view_html);comment_view.html(view_html);}).catch((err)=>{console.log(err.message);});}});$(document).on("submit","form.commentForm",function(e){e.preventDefault();let content=e.target[0].value;let{postId}=e.target.dataset;if(content){axios({method:"POST",url:"/api/comment/add",headers:{"X-CSRFTOKEN":Cookies.get("csrftoken"),"Content-Type":"application/json",},data:{content:content,post_id:postId},}).then((response)=>{let view_html=response.data.view;let post_wrapper=document.getElementById("posts-wrapper");post_wrapper.innerHTML=view_html;$("#lazyLoadLinkComments").hide();}).catch((err)=>{console.log(err.message);});}});$(document).on("submit","form.getMessageForm",function(e){e.preventDefault();let{messageId}=e.target.dataset;if(messageId){axios({method:"POST",url:"/api/messages/get",headers:{"X-CSRFTOKEN":Cookies.get("csrftoken"),"Content-Type":"application/json",},data:{message_id:parseInt(messageId),},}).then((response)=>{view_html=response.data.view;message_view.html(view_html);let converter=new showdown.Converter();$(document).ready(()=>{let message=document.getElementById("message-content-field");message.innerHTML=converter.makeHtml(message.innerHTML);});}).catch((err)=>{console.log(err.message);});}});;$("#raykomfi-register-form, #profile-form, #signin-form, #forgot-password-form, #create-post-form, #change-password-form").parsley().on("field:validated",function(e){console.log(this);});;axios.defaults.baseURL="http://localhost:8000";function w3_open(){document.getElementById("mySidebar").style.display="block";document.getElementById("myOverlay").style.display="block";}
function w3_close(){document.getElementById("mySidebar").style.display="none";document.getElementById("myOverlay").style.display="none";}
window.onscroll=function(){myFunction();};window.CSRF_TOKEN=document.getElementById("csrf_token").innerHTML;function myFunction(){if(document.body.scrollTop>80||document.documentElement.scrollTop>80){document.getElementById("myTop").classList.add("w3-card-4","w3-animate-opacity");document.getElementById("myIntro").classList.add("w3-show-inline-block");}else{document.getElementById("myIntro").classList.remove("w3-show-inline-block");document.getElementById("myTop").classList.remove("w3-card-4","w3-animate-opacity");}}
function myAccordion(id){var x=document.getElementById(id);if(x.className.indexOf("w3-show")==-1){x.className+=" w3-show";x.previousElementSibling.className+=" raykomfi-theme";}else{x.className=x.className.replace("w3-show","");x.previousElementSibling.className=x.previousElementSibling.className.replace(" raykomfi-theme","");}}
var modal=document.getElementById("myModal");var img=document.getElementById("myImg")||false;var modalImg=document.getElementById("modalImage");var captionText=document.getElementById("caption");if(img){img.onclick=function(){modal.style.display="block";modalImg.src=this.src;captionText.innerHTML=this.alt;};}
var span=document.getElementsByClassName("close")[0];if(img){$(document).on("click",function(event){if(!$(event.target).closest("#myImg").length){modal.style.display="none";}});}
$("#modalImage").on("click",function(event){event.stopPropagation();});$("html").addClass("hide-overflow");$(window).on("load",function(){$("html").removeClass("hide-overflow");$("#overlay").fadeOut(500);});var $loading=$("#sk-chase").hide();$(document).ajaxStart(function(){$loading.show();}).ajaxStop(function(){$loading.hide();});$("#new-message-content").on("keyup",(e)=>{let content=e.target.value;let converter=new showdown.Converter();content=converter.makeHtml(content);$("#message-preview").html(content);});;