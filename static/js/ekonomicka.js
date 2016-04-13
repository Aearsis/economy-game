$.ekonomicka = $.ekonomicka || {};

function formatByNum(num, one, two, more)
{
    return (num == 1 ? one : (num < 5 ? two : more));
}

function formatArray(strs) {
    var last = strs.pop();
    var before = strs.join(", ");
    if (before.length > 0)
        return before + " a " + last;
    else
        return last;
}

function naturalTime(secs) {
    var strs = [];
    if (secs == 0)
        return "právě teď";
    if (secs > 0) {
        var hour = Math.floor(secs / 3600);
        var min = Math.floor((secs % 3600) / 60);
        var sec = Math.floor(secs % 60);
        if (hour > 0 || min >= 5)
            sec = 0;
        if (hour != 0)
            strs.push(hour + formatByNum(hour, " hodinu", " hodiny", " hodin"));
        if (min != 0)
            strs.push(min + formatByNum(min, " minutu", " minuty", " minut"));
        if (sec != 0)
            strs.push(sec + formatByNum(sec, " vteřinu", " vteřiny", " vteřin"));
        return "za " + formatArray(strs);
    } else {
        secs *= -1;
        var hour = Math.floor(secs / 3600);
        var min = Math.floor((secs % 3600) / 60);
        var sec = Math.floor(secs % 60);
        if (hour > 0 || min >= 5)
            sec = 0;
        if (Math.max(hour, min, sec) == 0)
            return "právě teď";
        if (hour != 0)
            strs.push(hour + formatByNum(hour, " hodinou", " hodinami", " hodinami"));
        if (min != 0)
            strs.push(min + formatByNum(min, " minutou", " minutami", " minutami"));
        if (sec != 0)
            strs.push(sec + formatByNum(sec, " vteřinou", " vteřinami", " vteřinami"));
        return "před " + formatArray(strs);
    }
}

$(function () {
    $('[data-gametime]').each(function () {
        var time = parseInt($(this).attr('data-gametime')) + (new Date()).getSeconds();
        var formats = $(this).attr('data-gametime-format').split(";", 2);
        var el = $(this);
        setInterval(function () {
            var secs = time - (new Date()).getSeconds();
            el.text(formats[secs >= 0 ? 0 : 1].replace("%(natural)s", naturalTime(secs)));
        }, 100);
    });
});