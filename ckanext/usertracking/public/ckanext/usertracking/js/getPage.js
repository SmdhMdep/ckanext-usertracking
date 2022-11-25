// limit/offset paging buttons
function getPage(pageNo, currentName, formId) {
  document.getElementById(currentName).value = pageNo;
  document.getElementById(formId).submit();
}