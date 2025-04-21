pkgname=flatbat
pkgver=1.0
pkgrel=1
pkgdesc="Minimalist tkinter system monitor overlay (CPU, RAM, GPU, battery, and clock)"
arch=('any')
url="https://github.com/tomasmckenna/flatbat"
license=('MIT')
depends=('python' 'python-psutil' 'tk')
makedepends=('python-setuptools')
source=("flatbat/")
noextract=("flatbat/")
sha256sums=('SKIP')

package() {
    cd "$srcdir/flatbat"
    python setup.py install --root="$pkgdir/" --optimize=1
}

