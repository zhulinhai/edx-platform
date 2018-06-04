/* Javascript for StudioView. */
(function(define) {
    'use strict';

    var xblock;

    function createRocketChatDiscussion(data){
        var style = $(data)[0];
        xblock = $(data).find(".xblock-student_view-rocketc");
        $("head").append(style);
         $(".discussion-module").hide();
        if ($("div.discussion-module")[0] && !$(".page-content-main").find(".xblock-student_view-rocketc")[0]){
            $(".team-profile").find(".page-content-main").append(xblock);
        }else if ($(".page-content-main").find(".xblock-student_view-rocketc")[0]){
            $(".xblock-student_view-rocketc").replaceWith(xblock);
        }

    };

    function loadRocketChat(url){
        $.ajax({
            url: url,
            success: createRocketChatDiscussion
        });
    }

    function actionsReloadRocketChat(url){
        $( ".join-team .action" ).unbind().click(function() {
            loadRocketChat(url);
        });
        $( ".create-team .action" ).unbind().click(function() {
            loadRocketChat(url);
        });
        $( ".action-primary" ).unbind().click(function() {
            loadRocketChat(url);
        });
    }

    define(['jquery'],

        function($) {

            $(window).load(function() {

                $(".discussion-module").hide();
                var baseUrl = $(".container").attr("data-url");
                var url = baseUrl + "rocket-chat-discussion";
                loadRocketChat(url);
                actionsReloadRocketChat(url);

                var targetNode = $(".view-in-course")[0];

                // Options for the observer (which mutations to observe)
                var config = {subtree : true, attributes: true}

                // Callback function to execute when mutations are observed
                function fnHandler () {
                    if ($("div.discussion-module")[0] && !$(".page-content-main").find(".xblock-student_view-rocketc")[0]){
                        $(".discussion-module").hide();
                        $(".team-profile").find(".page-content-main").append(xblock);
                    }
                    actionsReloadRocketChat(url);
                }
                // Create an observer instance linked to the callback function
                var observer = new MutationObserver(fnHandler);

                // Start observing the target node for configured mutations
                observer.observe(targetNode, config);

            });

        });

}).call(this, define || RequireJS.define);
