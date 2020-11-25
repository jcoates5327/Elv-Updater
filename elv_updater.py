import requests
import os
import shutil
from zipfile import ZipFile


# replace with actual WoW directory
addon_dir = r'C:\Program Files (x86)\World of Warcraft\_retail_\Interface\Addons'

# elvui download page
elv_url = r'https://www.tukui.org/api.php?ui=elvui'


def main():
    if not os.path.exists(addon_dir):
        print('error: addon directory is missing')
        return

    # check currently installed version
    installed_ver = 0.0
    toc_path = os.path.join(addon_dir, 'ElvUI', 'ElvUI.toc')
    if os.path.exists(toc_path):
        installed_ver = get_cur_version(toc_path)
    print('installed version:', installed_ver)

    # make an API request for most recent ElvUI release info
    data = get_cur_release_info()
    if data is None:
        return

    # parse data
    current_ver = float(data['version'])
    url = data['url']
    print('latest version:', current_ver)

    # check if upgrade necessary
    if installed_ver < current_ver:
        ans = input('installation out of date, upgrade? y/n: ')
        if ans.lower() in ['yes', 'y']:
            print('upgrading...')
            res = download_files(url, current_ver)
            if res is None:
                print('unable to download files')
                return

            print('successfully downloaded updated files! cleaning up...')
            if installed_ver > 0.0:
                shutil.rmtree(os.path.join(addon_dir, 'ElvUI'))
                shutil.rmtree(os.path.join(addon_dir, 'ElvUI_OptionsUI'))

            print('copying new files...')
            with ZipFile(os.path.join(addon_dir, res)) as zf:
                zf.extractall(addon_dir)
            os.remove(os.path.join(addon_dir, res))
    else:
        print('installed version is current or higher, no upgrade necessary!')




# downloads into addon dir
# return name of zip file written
def download_files(url, current_ver):
    print('downloading:', url)  
    try:
        r = requests.get(url)
        status = r.status_code
        if status != 200:
            print('error: bad HTTP status code:', status)
        else:
            if r.content != '':
                fname = os.path.join(addon_dir, f'elvui-{current_ver}.zip')
                with open(fname, 'wb') as f:
                    f.write(r.content)
                return fname
            print('empty request content')
            return None
    except:
        print('HTTP request error, probably timeout')
    return None
    

def get_cur_release_info():
    print('requesting download page...')
    try:
        r = requests.get(elv_url)
        status = r.status_code
        if status != 200:
            print('error: bad HTTP status code:', status)
        else:
            if r.content != '':
                return r.json()
            print('empty request content')
            return None
    except:
        print('HTTP request error, probably timeout')

    return None


def get_cur_version(ver_file):
    with open(ver_file, 'r') as f:
        for line in f:
            if 'version' in line.lower():
                try:
                    ver = line.split(':')[1].strip()
                    return float(ver)
                except IndexError:
                    print('error splitting version num, index OOB')
                except ValueError:
                    print('error converting version string to float:', ver)
                break
    return None



if __name__ == '__main__':
    main()
