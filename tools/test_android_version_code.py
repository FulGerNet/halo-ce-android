"""Check Gradle's actual BuildConfig for absent, invalid and explicit build numbers."""
from pathlib import Path
import os, re, subprocess
root = Path(__file__).resolve().parent.parent
count = int(subprocess.check_output(['git','rev-list','--count','HEAD'],cwd=root,text=True).strip())
env = os.environ.copy()
env.setdefault('GRADLE_USER_HOME',str(root/'build/gradle-cache'))
env.setdefault('ANDROID_USER_HOME',str(root/'build/android-user'))
logs=root/'build/version-code-tests';logs.mkdir(parents=True,exist_ok=True)
for name,number,expected in [('unset',None,count),('blank','',count),('invalid','not-a-number',count),('explicit','3589',3589)]:
    if number is None:env.pop('HALO_BUILD_NUMBER',None)
    else:env['HALO_BUILD_NUMBER']=number
    command = ['cmd','/c','.\\gradlew.bat'] if os.name=='nt' else ['./gradlew']
    with (logs/(name+'.log')).open('w',encoding='utf-8') as log:
        subprocess.run([*command,'--console=plain',':app:generateDebugBuildConfig'],cwd=root/'port/android',env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    source=(root/'port/android/app/build/generated/source/buildConfig/debug/com/halo/decomp/BuildConfig.java').read_text()
    match=re.search(r'HALO_BUILD_NUMBER = (\d+);',source)
    assert match and int(match.group(1))==expected,(name,source,expected)
    print(name+': HALO_BUILD_NUMBER='+str(expected),flush=True)
