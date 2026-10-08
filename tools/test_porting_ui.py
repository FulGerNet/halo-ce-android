"""Run the actual UI text-box and porting draw functions against a recording renderer.

Uses the existing NDK and Node to execute a freestanding wasm test. No Android
device is needed for alpha/fade, glyph dispatch and background geometry checks.
GPU presentation still requires a device.
"""
from pathlib import Path
import re, shutil, subprocess

root = Path(__file__).resolve().parent.parent
out = root / 'build/porting-ui-tests'
out.mkdir(parents=True, exist_ok=True)
ndk = Path('C:/Android/ndk/29.0.14206865/toolchains/llvm/prebuilt/windows-x86_64/bin')

def function(path, name):
    source = (root / path).read_text()
    for match in reversed(list(re.finditer(r'\b'+name+r'\s*\(', source))):
        start = source.rfind('\n', 0, match.start())+1
        # Include the return type on the previous line if necessary.
        if source[start:match.start()].strip() == '':
            start = source.rfind('\n', 0, start-1)+1
        brace = source.find('{', match.end())
        semicolon = source.find(';', match.end())
        if brace < 0 or (semicolon >= 0 and semicolon < brace): continue
        depth = 1; end = brace+1
        while depth:
            depth += (source[end] == '{')-(source[end] == '}'); end += 1
        return source[start:end]
    raise ValueError(name)

prefix = r'''
typedef unsigned short wchar_t;
typedef float real;
typedef unsigned short word;
typedef int boolean;
#define NULL ((void*)0)
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define TEST_FLAG(a,b) ((a)&(1<<(b)))
#define NUMBER_OF_TEXT_JUSTIFICATIONS 3
#define _text_box_flashing_text_bit 0
#define _error_silent 0
#define FONT_GROUP_TAG 1
#define BITMAP_GROUP_TAG 2
#define SECONDS_PER_MILLISECOND 0.001f
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define PIN(v,a,b) MIN(MAX(v,a),b)
#define _ui_audio_feedback_cursor 0
typedef struct {short y0,x0,y1,x1;} rectangle2d;
typedef struct {short x,y;} point2d;
typedef struct {real alpha,red,green,blue;} real_argb_color;
struct tag_reference {long index;};
struct tag_block {long count; void *address;};
struct ui_widget_search_and_replace_reference {char search_string[32]; short replace_function;};
struct ui_widget_definition {
 struct tag_reference text_label_string_list,text_font,background_bitmap;
 struct tag_block search_and_replace_functions;
 rectangle2d bounds; short horizontal_offset,vertical_offset,string_list_index,justification;
 word text_box_flags; real_argb_color text_color;
};
struct widget_instance {
 struct widget_instance *parent; long definition_tag_index;
 struct widget_instance *child,*next;
 real alpha_modifier; boolean visible;
 struct {struct {wchar_t *text;short string_list_index;} text_box;} parameters;
};
static struct ui_widget_definition template;
'''+(root/'port/shared/include/halo_porting_ui.h').read_text()+r'''
'''+(root/'port/shared/include/halo_ui_pointer.h').read_text()+r'''
static struct halo_porting_menu ui_porting_menu;
static int ui_porting_context,ui_porting_count,ui_porting_revision;
static int ui_porting_scroll,ui_porting_scroll_max;
static int ui_porting_slider_action;
static rectangle2d ui_porting_slider_bounds, ui_porting_credit_bounds;
static boolean ui_porting_credit_visible, ui_porting_main_focus;
int ui_mouse_widget_has_focus(struct widget_instance *widget){return 0;}
#define UI_PORTING_TOP 112
#define UI_PORTING_BOTTOM 404
#define UI_PORTING_SCROLL_LEFT 590
#define UI_PORTING_SCROLL_RIGHT 626
static rectangle2d ui_porting_bounds[HALO_PORTING_ROWS];
static int ui_porting_actions[HALO_PORTING_ROWS];
static struct widget_instance fixture;
static struct widget_instance *ui_widget_port_error_text_box;
static wchar_t *ui_widget_port_error_text;
#define SPINNER_EXTRA_DESCRIPTION_BASE 1000
static wchar_t const *kills_to_win_extra_descriptions[] = {0};
struct ui_mouse_target {int kind; struct widget_instance *widget; rectangle2d bounds;};
#define _ui_mouse_target_item 0
static struct ui_mouse_target ui_mouse_targets[4];
static int ui_mouse_target_count, last_action, last_value, last_justification;
struct widget_instance *ui_mouse_menu(void){return &fixture;}
struct widget_instance *ui_porting_find_style(struct widget_instance *root){return root;}
struct widget_instance *ui_porting_find_text(struct widget_instance *root){return root;}
int ui_porting_is_quit(struct widget_instance *widget){return widget->definition_tag_index==99;}
void host_porting_action(int revision,int action,int value){last_action=action;last_value=value;}
void ui_play_audio_feedback_sound(int sound){}
void draw_quad(rectangle2d *bounds,unsigned long color){}
static struct {long current_system_milliseconds;} widget_globals;
static void *widget_memory_pool;
static int glyphs,percent,draw_percent,background_fixture,background_drawn;
static real_argb_color current_color;
static rectangle2d background_bounds;
struct bitmap_data {int width;};
int ui_widget_port_text_wrap(wchar_t *s,rectangle2d *b,short w){return 1;}
void draw_unicode_string_compute_bounds(rectangle2d *b,wchar_t *s,rectangle2d *t,rectangle2d *c){*t=*b;*c=*b;}
wchar_t *ustrncpy(wchar_t *d,wchar_t const *s,unsigned long n){unsigned long i=0;while(i<n&&s[i]){d[i]=s[i];++i;}return d;}
static struct bitmap_data blue;
void *memcpy(void *d,const void *s,unsigned long n) {char *a=d;const char*b=s;while(n--)*a++=*b++;return d;}
unsigned long ustrlen(wchar_t const*s){unsigned long n=0;while(s[n])++n;return n;}
char *strstr(char const*s,char const*q){for(;*s;++s){unsigned long n=0;while(q[n]&&q[n]==s[n])++n;if(!q[n])return (char*)s;}return NULL;}
int equal(char const*a,char const*b){while(*a&&*a==*b){++a;++b;}return *a==*b;}
wchar_t *ascii_to_wide(char const*s,wchar_t*d,unsigned long size){unsigned long n=0;while(s[n])++n;if(size<2*n+2)return NULL;for(unsigned long i=0;i<=n;++i)d[i]=s[i];return d;}
void *pool_resize_pointer(void*p,void*q,unsigned long n,char const*f,unsigned long l){return NULL;}
void csmemcpy(void*d,void const*s,unsigned long n){memcpy(d,s,n);}
wchar_t *unicode_string_list_get_string(long a,short b){return NULL;}
wchar_t *ui_widget_search_and_replace_invoke(struct widget_instance*w,short f){return NULL;}
long search_and_replace(wchar_t*a,wchar_t*b,wchar_t**c){return 0;}
void error(int level,char const*s){}
double cos(double x){return 0;}
int string_has_icons_to_draw(wchar_t*s){return 0;}
struct ui_widget_definition *ui_widget_definition_get(long tag){return &template;}
real_argb_color get_ui_argb_white(void){real_argb_color c={1,1,1,1};return c;}
void draw_string_set_draw_mode(long f,short s,short j,unsigned long flags,real_argb_color const*c){current_color=*c;last_justification=j;}
void draw_string_set_tab_stops(short const*p,short n){}
void draw_string_set_indents(short a,short b){}
void rasterizer_text_set_ui_scale(int x,int y,int p){percent=p;if(p!=100)draw_percent=p;}
int strcmp(char const*a,char const*b){while(*a&&*a==*b){++a;++b;}return *a-*b;}
char *strrchr(char const*s,int c){char *last=NULL;for(;*s;++s)if(*s==c)last=(char*)s;return last;}
int strncmp(char const*a,char const*b,unsigned long n){while(n&&*a&&*a==*b){++a;++b;--n;}return n?*a-*b:0;}
char const *tag_get_name(long tag){return tag==42?"ui\\shell\\pause_game\\pause_dialog_bkd":"ui\\shell\\pause_game\\button_key";}
void rasterizer_draw_unicode_string(rectangle2d const*b,rectangle2d const*c,point2d*p,short h,wchar_t const*s){
 if(current_color.alpha>0 && b->y0+17<b->y1 && b->x0<b->x1 && c->x0<c->x1 && c->y0<c->y1)glyphs+=(int)ustrlen(s);
}
void draw_string_and_hack_in_icons(rectangle2d*b,rectangle2d*c,point2d*p,short h,wchar_t const*s,boolean v){}
long halo_screen_width(void){return 1068;}
long tag_loaded(int group,char const*name){
 if(group==FONT_GROUP_TAG)return 1;
 if(background_fixture==0&&equal(name,"ui\\shell\\bitmaps\\blue"))return 10;
 if(background_fixture==1&&equal(name,"ui\\shell\\bitmaps\\pausebox_center"))return 11;
 return NONE;
}
struct bitmap_data *bitmap_group_get_bitmap_from_sequence(long t,int s,int f){return &blue;}
void draw_bitmap_in_rect(struct bitmap_data*b,rectangle2d*r,rectangle2d*s,rectangle2d*c,unsigned long color,void*p,boolean plain){
 background_bounds=*r;background_drawn=plain;
}
'''
code = prefix + '\n' + '\n'.join([
    function('source/interface/ui_widget.c','widget_instance_get_cumulative_alpha_modifier'),
    function('source/interface/ui_widget.c','widget_instance_render_text_box'),
    function('source/interface/ui_widget_porting.h','ui_porting_text'),
    function('source/interface/ui_widget_porting.h','ui_porting_adjust_widget'),
    function('source/interface/ui_widget_porting.h','ui_porting_background'),
    function('source/interface/ui_widget_porting.h','ui_porting_pointer'),
    function('source/interface/ui_widget_porting.h','ui_porting_render'),
]) + r'''
int run_tests(void){
 struct widget_instance parent={0},style={0};
 rectangle2d clip={0,0,480,640},row={356,192,389,448};
 template.text_label_string_list.index=NONE;template.text_font.index=1;template.justification=0;
 template.text_color.alpha=0;style.parent=&parent;style.alpha_modifier=0;style.visible=0;
 ui_porting_context=1;ui_porting_menu.page=0;glyphs=0;draw_percent=100;
 ui_porting_text(&style,"Porting options",row,&clip,TRUE,FALSE);
 if(glyphs!=15||current_color.alpha!=0.6f||percent!=100||last_justification!=2)return 1;
 if(draw_percent!=140||current_color.red!=0||current_color.green!=128.f/255.f||current_color.blue!=1)return 14;
 /* The old Quit row is replaced at exactly its native bounds, without an extra row. */
 fixture.definition_tag_index=99;fixture.parent=&parent;
 ui_mouse_target_count=1;ui_mouse_targets[0].kind=_ui_mouse_target_item;
 ui_mouse_targets[0].widget=&fixture;ui_mouse_targets[0].bounds=row;
 ui_porting_menu.revision=5;glyphs=0;
 ui_porting_render(&fixture,&clip);
 if(ui_porting_count!=1||ui_porting_bounds[0].y0!=356||ui_porting_bounds[0].y1!=389||glyphs!=15)return 16;
 struct halo_ui_pointer main_tap={0};main_tap.left_clicks=1;main_tap.click_x=320;main_tap.click_y=370;
 if(!ui_porting_pointer(&main_tap)||last_action!=1)return 17;
 ui_mouse_target_count=0;fixture.parent=NULL;
 ui_porting_context=2;
 struct widget_instance background={0};struct ui_widget_definition copy,*def=&template;point2d offset={320,240};
 background.parent=&parent;background.definition_tag_index=42;template.bounds.y1=200;
 if(!ui_porting_adjust_widget(&background,&def,&copy,&offset)||copy.bounds.y1!=(200+52)*112/100)return 15;
 ui_porting_context=2;row.y0=286;row.y1=313;glyphs=0;
 ui_porting_text(&style,"Overlay settings",row,&clip,TRUE,FALSE);
 if(glyphs!=16||current_color.alpha!=1)return 2;
 ui_porting_menu.page=6;row.x0=70;row.x1=570;row.y0=112;row.y1=156;glyphs=0;
 ui_porting_text(&style,"Invincibility [ON]",row,&clip,TRUE,FALSE);
 if(glyphs!=18||current_color.alpha!=1||current_color.green!=1)return 3;
 ui_porting_text(&style,"Gyroscope: unavailable",row,&clip,FALSE,FALSE);
 if(current_color.alpha!=0.45f||percent!=100)return 4;
 for(background_fixture=0;background_fixture<2;++background_fixture){
  background_drawn=0;ui_porting_background();
  if(!background_drawn||background_bounds.x0!=-214||background_bounds.x1!=854||background_bounds.y0!=0||background_bounds.y1!=480)return 5;
 }
 row.y0=60;row.y1=108;
 ui_porting_text(&style,"General",row,&clip,TRUE,TRUE);
 if(current_color.red!=0.35f||current_color.green!=0.8f)return 6;
 ui_porting_menu.count=65;ui_porting_menu.revision=8;
 for(int i=0;i<64;++i){memcpy(ui_porting_menu.rows[i].text,"Fire",5);ui_porting_menu.rows[i].action=1000+i;ui_porting_menu.rows[i].value=-1;}
 ui_porting_render(&fixture,&clip);
 if(ui_porting_scroll_max!=3548||ui_porting_count!=6)return 7;
 if(ui_porting_actions[ui_porting_count-1]!=90||ui_porting_bounds[ui_porting_count-1].y0!=420)return 8;
 struct halo_ui_pointer pointer={0};pointer.scroll_pixels=32767;last_action=0;
 if(!ui_porting_pointer(&pointer)||ui_porting_scroll!=3548||last_action)return 9;
 ui_porting_render(&fixture,&clip);
 pointer.scroll_pixels=0;pointer.left_clicks=1;pointer.click_x=100;pointer.click_y=365;
 ui_porting_pointer(&pointer);
 if(last_action!=1063)return 10;
 pointer.click_y=445;ui_porting_pointer(&pointer);
 if(last_action!=90)return 11;
 pointer.left_clicks=0;pointer.scroll_drag=1;pointer.x=608;pointer.y=112;last_action=0;
 ui_porting_pointer(&pointer);
 if(ui_porting_scroll!=0||last_action)return 12;
 pointer.scroll_drag=0;pointer.scroll_pixels=-32767;ui_porting_pointer(&pointer);
 if(ui_porting_scroll!=0)return 13;
 ui_porting_menu.page=4;ui_porting_menu.count=2;ui_porting_scroll=ui_porting_scroll_max=0;
 ui_porting_menu.rows[0].action=40;ui_porting_menu.rows[0].value=467;
 memcpy(ui_porting_menu.rows[0].text,"Look sensitivity",17);
 ui_porting_render(&fixture,&clip);
 pointer=(struct halo_ui_pointer){0};pointer.left_clicks=1;pointer.click_x=70;pointer.click_y=150;
 ui_porting_pointer(&pointer);if(last_action!=40||last_value!=0)return 18;
 ++ui_porting_menu.revision;pointer.scroll_drag=1;pointer.x=640;pointer.y=20;
 ui_porting_pointer(&pointer);if(last_value!=1000)return 19;
 pointer.x=0;ui_porting_pointer(&pointer);if(last_value!=0)return 20;
 ui_porting_context=1;ui_porting_menu.page=0;ui_porting_main_focus=TRUE;glyphs=0;
 ui_porting_text(&style,"Porting options",row,&clip,TRUE,FALSE);
 if(glyphs!=30||current_color.red!=1||current_color.blue!=1||current_color.alpha!=1)return 21;
 return 0;
}
'''
(out/'test.c').write_text(code)
subprocess.run([str(ndk/'clang.exe'),'--target=wasm32','-std=c99','-fshort-wchar','-ffreestanding','-fno-builtin','-c',str(out/'test.c'),'-o',str(out/'test.o')],check=True)
subprocess.run([str(ndk/'ld.lld.exe'),'-flavor','wasm','--no-entry','--export=run_tests',str(out/'test.o'),'-o',str(out/'test.wasm')],check=True)
(out/'run.cjs').write_text('const fs=require("fs"); const instance=new WebAssembly.Instance(new WebAssembly.Module(fs.readFileSync(__dirname+"/test.wasm"))); const result=instance.exports.run_tests(); if(result) throw new Error("UI regression "+result); console.log("Native text dispatch, centered labels, title color, bitmap bounds, 64-control scrolling and fixed Back passed");')
subprocess.run([shutil.which('node'),str(out/'run.cjs')],check=True)
