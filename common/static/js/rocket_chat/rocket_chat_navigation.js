(function(define) {
    'use strict';

    function loadComponents(pageContentMain, pageContentSecondary){
        if(window.location.hash == "#main"){
            pageContentSecondary.hide();
            pageContentMain.show();

        }else if (window.location.hash == "#settings"){
            pageContentMain.hide();
            pageContentSecondary.show();
        }
    }

    define(['jquery'],

        function($) {

            return function(options){

                var pageContentMain = $(".page-content-main");
                var pageContentSecondary = $(".page-content-secondary");
                var url_change_role = options["url_change_role"];

                loadComponents(pageContentMain, pageContentSecondary);
                window.location.href = "#main";

                $(window).bind('hashchange', function() {
                    loadComponents(pageContentMain, pageContentSecondary);
                });

                $(".change-role-rocketchat").unbind().click(function() {
                    var input = $(".rocket-chat-user-input")
                    var username = input.val();
                    var role = "coach";
                    $.ajax({
                        type: "POST",
                        url: url_change_role,
                        data: {username, role},
                        success: function(){
                            input.val("");
                            alert("The role has been changed");
                        },
                        error: function (request, status, error) {
                            alert(request.responseText);
                        },
                    });
                });
            };
        });

}).call(this, define || RequireJS.define);
