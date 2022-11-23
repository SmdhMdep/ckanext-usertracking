// cursor paging
function firstPage(formId){
  document.getElementById("user_engagement_direction").value = "first";
  document.getElementById("user_engagement_next_cursor").value = "";
  document.getElementById("user_engagement_prev_cursor").value = null;
  document.getElementById(formId).submit();
}

function prevPage(formId){
  document.getElementById("user_engagement_direction").value = "backward";
  document.getElementById(formId).submit();
}

function nextPage(formId){
  document.getElementById("user_engagement_direction").value = "fordward";
  document.getElementById(formId).submit();
}


// limit/offset paging
function getPage(pageNo, currentName, formId) {
  document.getElementById(currentName).value = pageNo;
  document.getElementById(formId).submit();
}