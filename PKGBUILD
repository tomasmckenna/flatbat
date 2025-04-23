# Maintainer: Your Name <your.email@example.com>

pkgname=flatbat
pkgver=1.0.0
pkgrel=1
pkgdesc="Minimalist tkinter system monitor overlay (CPU, RAM, GPU, battery, and clock)"
arch=('any')
url="https://github.com/tomasmckenna/flatbat"
license=('MIT')
depends=('python' 'python-psutil' 'tk')
makedepends=('python-setuptools' 'python-pip' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::https://github.com/tomasmckenna/$pkgname/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('60f36a10305b4e4e6a83e1060fe0c274cb32b7bd64724ffae24a223b5d5facde')

package() {
    cd "$srcdir/$pkgname-$pkgver"
    python setup.py install --root="$pkgdir/" --optimize=1
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}