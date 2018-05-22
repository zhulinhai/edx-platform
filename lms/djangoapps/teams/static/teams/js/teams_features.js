/* Javascript for StudioView. */
(function(define) {
    'use strict';
    define(['jquery'],

        function($) {

            var xblock = $(".rocketc_block");
            var sga = $(".sga-block")
            $(".hidden-rocket-chat").hide()

            $(window).load(function() {

                $("div.discussion-module").replaceWith(xblock);
                $(".loading-animation").hide()

                var targetNode = $(".teams-content")[0];
                debugger;

                // Options for the observer (which mutations to observe)
                var config = {subtree : true, attributes: true}

                // Callback function to execute when mutations are observed
                function fnHandler () {
                    if($("div.discussion-module")[0]){
                        $("div.discussion-module").replaceWith(xblock);
                        $(".loading-animation").hide()
                    }
                    if($("div.page-content-secondary")[0]){
                        if(! $('.page-content-secondary').find('.sga-block').length){                            
                        $("div.page-content-secondary").append(sga);}
                    }


                }
                // Create an observer instance linked to the callback function
                var observer = new MutationObserver(fnHandler);

                // Start observing the target node for configured mutations
                observer.observe(targetNode, config);

            });

        });
}).call(this, define || RequireJS.define);


var RuntimeProvider = (function() {

  var getRuntime = function(version) {
    if (! this.versions.hasOwnProperty(version)) {
      throw 'Unsupported XBlock version: ' + version;
    }
    return this.versions[version];
  };

  var versions = {
    1: {
      handlerUrl: function(block, handlerName, suffix, query) {
        suffix = typeof suffix !== 'undefined' ? suffix : '';
        query = typeof query !== 'undefined' ? query : '';
        var usage = $(block).data('usage');
        var url_selector = $(block).data('url_selector');
        if (url_selector !== undefined) {
            baseUrl = window[url_selector];
        }
        else {baseUrl = handlerBaseUrl;}

        // studentId and handlerBaseUrl are both defined in block.html
        return (baseUrl + usage +
                           "/" + handlerName +
                           "/" + suffix +
                   "?student=" + studentId +
                           "&" + query);
      },
      children: function(block) {
        return $(block).prop('xblock_children');
      },
      childMap: function(block, childName) {
        var children = this.children(block);
        for (var i = 0; i < children.length; i++) {
          var child = children[i];
          if (child.name == childName) {
            return child
          }
        }
      }
    }
  };

  return {
    getRuntime: getRuntime,
    versions: versions
  };
}());
