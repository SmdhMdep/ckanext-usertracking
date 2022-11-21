ckan.module('tracking2', function ($) {
    return {
      initialize: function () {

        //Hold userdata till they leave page
        window.id = this.options.id;
        window.Username = this.options.name;

        // Tracking
        var url = location.pathname;
        // remove any site root from url
        url = url.substring($('body').data('locale-root'), url.length);
        // trim any trailing /
        url = url.replace(/\/*$/, '');
        window.pathurl = url

      }
    };
  }
);

TimeMe.initialize({
  currentPageName: "Test", // current page
  idleTimeoutInSeconds: 30 // seconds
});

window.onbeforeunload = function() {

  //Get time on page
  let timeSpentOnPage = TimeMe.getTimeOnCurrentPageInSeconds();
  
  // Gets userdata from the tracking2 module
  var id = window.id;
  var Username = window.Username;
  var url = window.pathurl
  
  
  //Information will be here
  //username can be found in "Username" var
  $.ajax({url : $('body').data('site-root') + '_usertracking',
          type : 'POST',
          data : {url:url, type:'page', id:id, name:Username, time:timeSpentOnPage},
          timeout : 300 });
  $('a.resource-url-analytics').on('click', function (e){
    var url = $(e.target).closest('a').attr('href');
    $.ajax({url : $('body').data('site-root') + '_usertracking',
            data : {url:url, type:'resource', id:id, name:Username, time:timeSpentOnPage},
            type : 'POST',
            timeout : 30});
  }
  );
}

