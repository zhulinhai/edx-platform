/* Javascript for StudioView. */
(function(define) {
    'use strict';

    var xblock;
    var teams;

    function createRocketChatDiscussion(urlRocketChat){


        var iframe = $('<iframe>', {
            src: urlRocketChat,
            id:  "rocketChatXblock",
            style: "width: 100%; border: none;",
            scrolling: 'no'
            });

        iframe.load(function() {
            $(this).height( $(this).contents().find("body").height() );
        });

        $(".discussion-module").hide();
        if ($("div.discussion-module")[0] && !$(".page-content-main").find("#rocketChatXblock")[0]){
            $(".team-profile").find(".page-content-main").append(iframe);
        }else if ($(".page-content-main").find("#rocketChatXblock")[0]){
            $("#rocketChatXblock").attr("src", urlRocketChat)
        }
        xblock = iframe;
    };

    function actionsButtons(urlRocketChat){
        $( ".join-team .action" ).unbind().click(function() {
            createRocketChatDiscussion(urlRocketChat);
        });
        $( ".create-team .action" ).unbind().click(function() {
            createRocketChatDiscussion(urlRocketChat);
        });
        $( ".action-primary" ).unbind().click(function() {
            createRocketChatDiscussion(urlRocketChat);
        });
    };

    function loadUserTeam(options){
        var data = {"course_id": options.courseID, "username": options.userInfo.username}
        $.ajax({
            url: options.teamsUrl,
            data: data,
            success: function(data){
                teams = data;
            }
        });
    };

    function removeBrowseTab(teams){
        if (teams.count == 1){
            $("#tab-1").remove();
            $("#tabpanel-browse").remove();
            $("#tab-0").addClass("is-active");
            $("#tabpanel-my-teams").removeClass("is-hidden");
        }
    };

    function buttonAddMembers(staff, url){
        var button = $("<button class='btn btn-secondary'>Add Members</button>");
        var input = $("<input type='file' name='fileUpload' style='display: none;'accept='text/csv'/>")
        if(!$(".page-header-secondary").children()[0] && staff){
            $(".page-header-secondary").append(input);
            $(".page-header-secondary").append(button);

            input.fileupload({
                url: url,
                done:function(e, data){
                    $(".page-header-secondary").empty();
                    buttonAddMembers(staff, url);
                    var errors = data.result.errors;
                    var success = data.result.success;
                    var container = $("<div title='Result'></div>");
                    var list = $("<ul></ul>");

                    for (var key in errors){
                        var item = $("<li style='color: red; font-size:12px;'>Error in "+key+" = "+errors[key]+"</li>");
                        list.append(item);
                    };

                    container.append(list);
                    var list = $("<ul></ul>");

                    for (var key in success){
                        var item = $("<li style='color: green; font-size:12px;'>"+success[key]+"</li>");
                        list.append(item);
                    };

                    container.append(list);
                    container.dialog();
                },
                fail: function(e, data){
                    $(".page-header-secondary").empty();
                    buttonAddMembers(staff, url);
                    var container = $("<div title='Result'>"+data.errorThrown+"</div>");
                    container.dialog();
                }
            });

            button.click(function(){
                input.click();
            });
        }
    }

    function loadjs(url) {
        $('<script>')
            .attr('type', 'text/javascript')
            .attr('src', url)
            .appendTo("body");
    }

    define(['jquery'],

        function($) {

            loadjs('/static/js/vendor/jQuery-File-Upload/js/vendor/jquery.ui.widget.js');
            loadjs('/static/js/vendor/jQuery-File-Upload/js/jquery.fileupload.js');
            loadjs('/static/js/vendor/jquery-ui.min.js');

            return function(options){
                var urlRocketChat = "/xblock/"+options.rocketChatLocator;
                var urlApiCreateTeams = options.teamsCreateUrl;
                var staff = options.userInfo.staff;
                teams = options.userInfo.teams;

                $(window).load(function() {

                    $(".discussion-module").hide();

                    createRocketChatDiscussion(urlRocketChat);
                    actionsButtons(urlRocketChat);
                    removeBrowseTab(teams);
                    buttonAddMembers(staff, urlApiCreateTeams);

                    var targetNode = $(".view-in-course")[0];

                    // Options for the observer (which mutations to observe)
                    var config = {subtree : true, attributes: true}

                    // Callback function to execute when mutations are observed
                    function fnHandler () {
                        if ($("div.discussion-module")[0] && !$(".page-content-main").find("#rocketChatXblock")[0]){
                            $(".discussion-module").hide();
                            $(".team-profile").find(".page-content-main").append(xblock);
                        }
                        loadUserTeam(options);
                        actionsButtons(urlRocketChat);
                        removeBrowseTab(teams);
                        buttonAddMembers(staff, urlApiCreateTeams);
                    }
                    // Create an observer instance linked to the callback function
                    var observer = new MutationObserver(fnHandler);

                    // Start observing the target node for configured mutations
                    observer.observe(targetNode, config);

                });

            };
        });

}).call(this, define || RequireJS.define);
