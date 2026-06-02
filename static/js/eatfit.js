(function () {
    function setMenuOpen(root, open) {
        const button = root.querySelector('[data-menu-button]');
        const panel = root.querySelector('[data-menu-panel]');
        if (!button || !panel) {
            return;
        }
        button.setAttribute('aria-expanded', open ? 'true' : 'false');
        panel.hidden = !open;
    }

    function setupMenus() {
        document.querySelectorAll('[data-menu-root]').forEach((root) => {
            const button = root.querySelector('[data-menu-button]');
            if (!button) {
                return;
            }
            button.addEventListener('click', () => {
                const isOpen = button.getAttribute('aria-expanded') === 'true';
                setMenuOpen(root, !isOpen);
            });
        });

        document.addEventListener('click', (event) => {
            document.querySelectorAll('[data-menu-root]').forEach((root) => {
                if (!root.contains(event.target)) {
                    setMenuOpen(root, false);
                }
            });
        });
    }

    function setupEntryTypeToggles() {
        document.querySelectorAll('[data-entry-type-root]').forEach((root) => {
            const select = root.querySelector('[data-entry-type-select]');
            if (!select) {
                return;
            }
            const update = () => {
                root.querySelectorAll('[data-entry-section]').forEach((section) => {
                    section.hidden = section.dataset.entrySection !== select.value;
                });
            };
            select.addEventListener('change', update);
            update();
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        setupMenus();
        setupEntryTypeToggles();
    });
})();
