# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.


"""
This file declares all core JS/CSS assets used by Indico
"""

# stdlib imports
import os
from urlparse import urlparse

# 3rd party libs
from markupsafe import Markup
from webassets import Bundle, Environment

# legacy imports
from indico.core.config import Config


def configure_pyscss(environment):
    config = Config.getInstance()
    base_url_path = urlparse(config.getBaseURL()).path
    environment.config['PYSCSS_DEBUG_INFO'] = environment.debug and config.getSCSSDebugInfo()
    environment.config['PYSCSS_STATIC_URL'] = '{0}/static/'.format(base_url_path)
    environment.config['PYSCSS_LOAD_PATHS'] = [
        os.path.join(config.getHtdocsDir(), 'sass', 'lib', 'compass'),
        os.path.join(config.getHtdocsDir(), 'sass')
    ]


class IndicoEnvironment(Environment):
    def __init__(self):
        config = Config.getInstance()
        url_path = urlparse(config.getBaseURL()).path
        output_dir = os.path.join(config.getHtdocsDir(), 'static', 'assets')
        url = '{0}/static/assets/'.format(url_path)

        super(IndicoEnvironment, self).__init__(output_dir, url)
        self.debug = config.getDebug()
        configure_pyscss(self)

        self.append_path(config.getHtdocsDir(), '/')
        self.append_path(os.path.join(config.getHtdocsDir(), 'css'), '{0}/css'.format(url_path))
        self.append_path(os.path.join(config.getHtdocsDir(), 'js'), '{0}/js'.format(url_path))


def namespace(dir_ns, *list_files):
    return [os.path.join(dir_ns, f) for f in list_files]


def include_js_assets(bundle_name):
    """Jinja template function to generate HTML tags for a JS asset bundle."""
    return Markup('\n'.join('<script src="{}"></script>'.format(url) for url in core_env[bundle_name].urls()))


def include_css_assets(bundle_name):
    """Jinja template function to generate HTML tags for a CSS asset bundle."""
    return Markup('\n'.join('<link rel="stylesheet" type="text/css" href="{}">'.format(url)
                            for url in core_env[bundle_name].urls()))


def rjs_bundle(name, *files):
    return Bundle(*files, filters='rjsmin', output='js/{}_%(version)s.min.js'.format(name))


indico_core = rjs_bundle(
    'indico_core',
    *namespace('js/indico/Core',

               'Presentation.js',
               'Data.js',
               'Components.js',
               'Auxiliar.js',
               'Buttons.js',
               'Effects.js',
               'Interaction/Base.js',
               'Widgets/Base.js',
               'Widgets/Inline.js',
               'Widgets/DateTime.js',
               'Widgets/Menu.js',
               'Widgets/RichText.js',
               'Widgets/Navigation.js',
               'Widgets/UserList.js',
               'Dialogs/Popup.js',
               'Dialogs/PopupWidgets.js',
               'Dialogs/Base.js',
               'Dialogs/Util.js',
               'Dialogs/Users.js',
               'Dialogs/PopupWidgets.js',
               'Browser.js',
               'Services.js',
               'Util.js',
               'Login.js',
               'Dragndrop.js',
               'keymap.js'))

indico_management = rjs_bundle(
    'indico_management',
    *namespace('js/indico/Management',

               'ConfModifDisplay.js',
               'RoomBooking.js',
               'eventCreation.js',
               'Timetable.js',
               'AbstractReviewing.js',
               'NotificationTPL.js',
               'Registration.js',
               'Contributions.js',
               'Sessions.js',
               'CFA.js',
               'RoomBookingMapOfRooms.js',
               'EventUsers.js'))

indico_room_booking = rjs_bundle(
    'indico_room_booking',
    'js/lib/rrule.js',
    *namespace('js/indico/RoomBooking',

               'util.js',
               'MapOfRooms.js',
               'BookingForm.js',
               'RoomBookingCalendar.js',
               'roomselector.js',
               'validation.js'))

indico_admin = rjs_bundle(
    'indico_admin',
    *namespace('js/indico/Admin',

               'News.js',
               'Upcoming.js'))

indico_timetable = rjs_bundle(
    'indico_timetable',
    *namespace('js/indico/Timetable',

               'Filter.js',
               'Layout.js',
               'Undo.js',
               'Base.js',
               'DragAndDrop.js',
               'Draw.js',
               'Management.js'))

indico_legacy = rjs_bundle(
    'indico_legacy',
    *namespace('js/indico/Legacy',

               'Widgets.js',
               'Dialogs.js',
               'Util.js'))

indico_common = rjs_bundle(
    'indico_common',
    *namespace('js/indico/Common',
               'Export.js',
               'TimezoneSelector.js',
               'Social.js',
               'htmlparser.js'))

indico_materialeditor = rjs_bundle('indico_materialeditor', 'js/indico/MaterialEditor/Editor.js')

indico_display = rjs_bundle('indico_display', 'js/indico/Display/Dialogs.js')

indico_jquery = rjs_bundle(
    'indico_jquery',
    *namespace('js/indico/jquery',
               'defaults.js',
               'global.js',
               'errors.js',
               'ajaxcheckbox.js',
               'ajaxdialog.js',
               'clearableinput.js',
               'actioninput.js',
               'fieldarea.js',
               'multiselect.js',
               'principalfield.js',
               'realtimefilter.js',
               'scrollblocker.js',
               'timerange.js',
               'tooltips.js'))

indico_jquery_authors = rjs_bundle('indico_jquery_authors', 'js/indico/jquery/authors.js')

indico_badges_js = rjs_bundle('indico_badges', 'js/indico/Management/ConfModifBadgePosterPrinting.js')

indico_badges_css = Bundle('css/badges.css',
                           filters='cssmin', output='css/indico_badges_%(version)s.min.css')

indico_regform = rjs_bundle(
    'indico_regform',
    *namespace('js/indico/RegistrationForm',
               'registrationform.js',
               'section.js',
               'field.js',
               'sectiontoolbar.js',
               'table.js'))

angular = rjs_bundle(
    'angular',
    'js/lib/angular.js',
    'js/lib/angular-resource.js',
    'js/lib/angular-sanitize.js',
    'js/lib/sortable.js',
    'js/indico/angular/app.js',
    'js/indico/angular/directives.js',
    'js/indico/angular/filters.js',
    'js/indico/angular/services.js')

zero_clipboard_js = rjs_bundle('zero_clipboard_js',
                               'js/lib/zeroclipboard/ZeroClipboard.js',
                               'js/custom/zeroclipboard.js')

selectize_js = rjs_bundle('selectize_js',
                          'js/lib/selectize.js/selectize.js')

selectize_css = Bundle('css/lib/selectize.js/selectize.css',
                       'css/lib/selectize.js/selectize.default.css',
                       filters='cssmin', output='css/selectize_css_%(version)s.min.css')

jquery = rjs_bundle('jquery', *filter(None, [
    'js/lib/underscore.js',
    'js/lib/jquery.js',
    'js/lib/jquery.qtip.js',
    'js/jquery/jquery-ui.js',
    'js/lib/jquery.multiselect.js',
    'js/lib/jquery.multiselect.filter.js',
    'js/jquery/jquery-migrate-silencer.js' if not Config.getInstance().getDebug() else None] +
    namespace('js/jquery',

              'jquery-migrate.js',
              'jquery.form.js',
              'jquery.custom.js',
              'jquery.daterange.js',
              'jquery.dttbutton.js',
              'jquery.colorbox.js',
              'jquery.menu.js',
              'date.js',
              'jquery.colorpicker.js',
              'jquery-extra-selectors.js',
              'jquery.typewatch.js',
              'jstorage.js',
              'jquery.placeholder.js')))

utils = rjs_bundle('utils', *namespace('js/utils', 'routing.js', 'i18n.js', 'misc.js', 'forms.js'))
calendar = rjs_bundle('calendar', *namespace('js/calendar', 'calendar.js', 'calendar-setup.js'))

presentation = rjs_bundle(
    'presentation',
    *namespace('js/presentation',

               'Core/Primitives.js',
               'Core/Iterators.js',
               'Core/Tools.js',
               'Core/String.js',
               'Core/Type.js',
               'Core/Interfaces.js',
               'Core/Commands.js',
               'Core/MathEx.js',
               'Data/Bag.js',
               'Data/Watch.js',
               'Data/WatchValue.js',
               'Data/WatchList.js',
               'Data/WatchObject.js',
               'Data/Binding.js',
               'Data/Logic.js',
               'Data/Json.js',
               'Data/Remote.js',
               'Data/DateTime.js',
               'Ui/MimeTypes.js',
               'Ui/XElement.js',
               'Ui/Html.js',
               'Ui/Dom.js',
               'Ui/Style.js',
               'Ui/Extensions/Lookup.js',
               'Ui/Extensions/Layout.js',
               'Ui/Text.js',
               'Ui/Styles/SimpleStyles.js',
               'Ui/Widgets/WidgetBase.js',
               'Ui/Widgets/WidgetPage.js',
               'Ui/Widgets/WidgetComponents.js',
               'Ui/Widgets/WidgetControl.js',
               'Ui/Widgets/WidgetEditor.js',
               'Ui/Widgets/WidgetTable.js',
               'Ui/Widgets/WidgetField.js',
               'Ui/Widgets/WidgetEditable.js',
               'Ui/Widgets/WidgetMenu.js',
               'Ui/Widgets/WidgetGrid.js'))

ie_compatibility = rjs_bundle('ie_compatibility', 'js/selectivizr.js')

jed = rjs_bundle('jed', 'js/lib/jed.js')
moment = rjs_bundle('moment', *namespace('js/moment', 'moment.js', 'locale/es.js', 'locale/fr.js'))

jqplot_js = rjs_bundle('jqplot',
                       *namespace('js/lib/jqplot',
                                  'core/jqplot.core.js',
                                  'core/jqplot.linearTickGenerator.js',
                                  'core/jqplot.linearAxisRenderer.js',
                                  'core/jqplot.axisTickRenderer.js',
                                  'core/jqplot.axisLabelRenderer.js',
                                  'core/jqplot.tableLegendRenderer.js',
                                  'core/jqplot.lineRenderer.js',
                                  'core/jqplot.markerRenderer.js',
                                  'core/jqplot.divTitleRenderer.js',
                                  'core/jqplot.canvasGridRenderer.js',
                                  'core/jqplot.linePattern.js',
                                  'core/jqplot.shadowRenderer.js',
                                  'core/jqplot.shapeRenderer.js',
                                  'core/jqplot.sprintf.js',
                                  'core/jsdate.js',
                                  'core/jqplot.themeEngine.js',
                                  'core/jqplot.toImage.js',
                                  'core/jqplot.effects.core.js',
                                  'core/jqplot.effects.blind.js',
                                  # hardcoded list since globbing doesn't have a fixed order across machines
                                  'plugins/axis/jqplot.canvasAxisLabelRenderer.js',
                                  'plugins/axis/jqplot.canvasAxisTickRenderer.js',
                                  'plugins/axis/jqplot.categoryAxisRenderer.js',
                                  'plugins/axis/jqplot.dateAxisRenderer.js',
                                  'plugins/axis/jqplot.logAxisRenderer.js',
                                  'plugins/bar/jqplot.barRenderer.js',
                                  'plugins/cursor/jqplot.cursor.js',
                                  'plugins/highlighter/jqplot.highlighter.js',
                                  'plugins/points/jqplot.pointLabels.js',
                                  'plugins/text/jqplot.canvasTextRenderer.js'))

jqplot_css = Bundle(
    'css/lib/jquery.jqplot.css',
    filters='cssmin', output='css/jqplot_%(version)s.min.css'
)

mathjax_js = rjs_bundle('mathjax', 'js/lib/mathjax/MathJax.js', 'js/custom/pagedown_mathjax.js')
contributions_js = rjs_bundle('contributions', 'js/indico/Display/contributions.js')

abstracts_js = rjs_bundle(
    'abstracts',
    contributions_js,
    'js/indico/Management/abstracts.js',
    *namespace('js/lib/pagedown',
               'Markdown.Converter.js',
               'Markdown.Editor.js',
               'Markdown.Sanitizer.js'))

base_js = Bundle(jquery, angular, jed, utils, presentation, calendar, indico_jquery, moment,
                 indico_core, indico_legacy, indico_common)

module_js = {
    'vc': rjs_bundle('modules_vc', 'js/indico/modules/vc.js'),
    'event_display': rjs_bundle('modules_event_display', 'js/indico/modules/eventdisplay.js')
}

SASS_BASE_MODULES = ["sass/*.scss",
                     "sass/base/*.scss",
                     "sass/custom/*.scss",
                     "sass/partials/*.scss"]


def sass_module_bundle(module_name, depends=[]):
    return Bundle('sass/modules/_{0}.scss'.format(module_name),
                  filters=("pyscss", "cssrewrite", "cssmin"),
                  output="sass/{0}_%(version)s.min.css".format(module_name),
                  depends = SASS_BASE_MODULES + ['sass/modules/{0}/*.scss'.format(module_name)] + depends)

agreements_sass = sass_module_bundle('agreements')
contributions_sass = sass_module_bundle('contributions')
registrationform_sass = sass_module_bundle('registrationform')
roombooking_sass = sass_module_bundle('roombooking')
dashboard_sass = sass_module_bundle('dashboard')
category_sass = sass_module_bundle('category')
admin_sass = sass_module_bundle('admin')
eventservices_sass = sass_module_bundle('eventservices')
event_display_sass = sass_module_bundle('event_display')
event_management_sass = sass_module_bundle('event_management')
overviews_sass = sass_module_bundle('overviews')
vc_sass = sass_module_bundle('vc')
news_sass = sass_module_bundle('news')
users_sass = sass_module_bundle('users')
auth_sass = sass_module_bundle('auth')

screen_sass = Bundle('sass/screen.scss',
                     filters=("pyscss", "cssrewrite", "cssmin"),
                     output="sass/screen_sass_%(version)s.css",
                     depends=SASS_BASE_MODULES)


def register_all_js(env):
    env.register('jquery', jquery)
    env.register('utils', utils)
    env.register('presentation', presentation)
    env.register('indico_core', indico_core)
    env.register('indico_management', indico_management)
    env.register('indico_roombooking', indico_room_booking)
    env.register('indico_admin', indico_admin)
    env.register('indico_timetable', indico_timetable)
    env.register('indico_legacy', indico_legacy)
    env.register('indico_common', indico_common)
    env.register('indico_materialeditor', indico_materialeditor)
    env.register('indico_display', indico_display)
    env.register('indico_jquery', indico_jquery)
    env.register('indico_authors', indico_jquery_authors)
    env.register('indico_badges_js', indico_badges_js)
    env.register('indico_regform', indico_regform)
    env.register('base_js', base_js)
    env.register('ie_compatibility', ie_compatibility)
    env.register('abstracts_js', abstracts_js)
    env.register('contributions_js', contributions_js)
    env.register('mathjax_js', mathjax_js)
    env.register('jqplot_js', jqplot_js)
    env.register('zero_clipboard_js', zero_clipboard_js)
    env.register('selectize_js', selectize_js)

    for key, bundle in module_js.iteritems():
        env.register('modules_{}_js'.format(key), bundle)


def register_all_css(env, main_css_file):

    base_css = Bundle(
        *namespace('css',
                   main_css_file,
                   'calendar-blue.css',
                   'jquery-ui.css',
                   'lib/angular.css',
                   'lib/jquery.qtip.css',
                   'lib/jquery.multiselect.css',
                   'lib/jquery.multiselect.filter.css',
                   'jquery.colorbox.css',
                   'jquery-ui-custom.css',
                   'jquery.qtip-custom.css',
                   'jquery.colorpicker.css'),
        filters=("cssmin", "cssrewrite"),
        output='css/base_%(version)s.min.css')

    env.register('base_css', base_css)
    env.register('indico_badges_css', indico_badges_css)
    env.register('jqplot_css', jqplot_css)
    env.register('selectize_css', selectize_css)

    # SASS/SCSS
    env.register('agreements_sass', agreements_sass)
    env.register('registrationform_sass', registrationform_sass)
    env.register('roombooking_sass', roombooking_sass)
    env.register('contributions_sass', contributions_sass)
    env.register('dashboard_sass', dashboard_sass)
    env.register('category_sass', category_sass)
    env.register('admin_sass', admin_sass)
    env.register('screen_sass', screen_sass)
    env.register('eventservices_sass', eventservices_sass)
    env.register('event_display_sass', event_display_sass)
    env.register('event_management_sass', event_management_sass)
    env.register('overviews_sass', overviews_sass)
    env.register('vc_sass', vc_sass)
    env.register('news_sass', news_sass)
    env.register('users_sass', users_sass)
    env.register('auth_sass', auth_sass)


core_env = IndicoEnvironment()
