var App = new function() {
    var _modules = {};
    this.module = function(key) {
        if(!_modules[key]) {
            _modules[key] = {};
        }
        return _modules[key];
    }
    this.template = function(key) {
        var template = null;
        function result(context) {
            if(template == null) {
                $el = $('#' + key)
                console.assert($el.size() == 1, 'Template not found: ' + key)
                template = _.template(
                    $('#' + key).html());
            }
            return template(context);
        }
        return result;
    }
};
