
ckan.module('tracking', function ($) {
  return {
    initialize: function () {

      // Access some options passed to this JavaScript module by the calling
      // template.
      var id = this.options.id;
      var Username = this.options.name;

      // Tracking
      var url = location.pathname;
      // remove any site root from url
      url = url.substring($('body').data('locale-root'), url.length);
      // trim any trailing /
      url = url.replace(/\/*$/, '');

      //Information will be here
      //username can be found in "Username" var

      $.ajax({url : $('body').data('site-root') + '_usertracking',
              type : 'POST',
              data : {url:url, type:'page', id:id},
              timeout : 300 });
      $('a.resource-url-analytics').on('click', function (e){
        var url = $(e.target).closest('a').attr('href');
        $.ajax({url : $('body').data('site-root') + '_usertracking',
                data : {url:url, type:'resource', id:id },
                type : 'POST',
                timeout : 30});
      });

    }
  };
});


