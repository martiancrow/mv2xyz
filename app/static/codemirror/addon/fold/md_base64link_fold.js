// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: https://codemirror.net/LICENSE

(function(mod) {
    if (typeof exports == "object" && typeof module == "object") // CommonJS
        mod(require("../../lib/codemirror"));
    else if (typeof define == "function" && define.amd) // AMD
        define(["../../lib/codemirror"], mod);
    else // Plain browser env
        mod(CodeMirror);
})(function(CodeMirror) {
"use strict";

    CodeMirror.registerHelper("fold", "markdown", function(cm, start) {

        function isBase64Link(lineNo) {
            var txt = cm.getLine(lineNo)

            if (/^.*\!?\[.*\]\((data:){1}.*(base64){1}.*\).*/gi.test(txt)) {
                return true;
            }

            return false;

        }

        function getCutRange(lineNo) {
            var txt = cm.getLine(lineNo)

            var startstr = txt.match(/^.*?\!?\[.*?\]\(data:.*?base64/gi)[0];

            return {
                cutstart: startstr.length,
                cutend: txt.length - 1
            }

        }

        if (isBase64Link(start.line)) {

            var range = getCutRange(start.line);

            //换到插入时操作

            return {
                from: CodeMirror.Pos(start.line, range.cutstart),
                to: CodeMirror.Pos(start.line, range.cutend)
            };
        }


        return null;

        
    });

});
