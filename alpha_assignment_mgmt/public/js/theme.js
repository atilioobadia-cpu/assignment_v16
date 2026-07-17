function applyTheme() {
	var root = document.documentElement;
	var isDark = root.getAttribute("data-theme") === "dark" || root.getAttribute("data-theme-mode") === "dark";
	var vars = isDark
		? {
			"--primary": "#2B5129",
			"--primary-color": "#2B5129",
			"--brand-color": "#2B5129",
			"--btn-primary": "#2B5129",
			"--btn-primary-text-color": "#FFFFFF",
			"--border-primary": "#2B5129",

			"--surface-gray-7": "#1A1C1A",
			"--bg-color": "#1A1C1A",
			"--layout-bg": "#1A1C1A",

			"--surface-menu-bar": "#111211",
			"--navbar-bg": "#111211",
			"--surface-white": "#111211",

			"--surface-modal": "#2B5129",
			"--card-bg": "#2B5129",
			"--fg-color": "#2B5129",
			"--control-bg": "#2B5129",

			"--surface-gray-1": "#1A1C1A",
			"--sidebar-bg": "#1A1C1A",

			"--ink-gray-9": "#FFFFFF",
			"--text-color": "#FFFFFF",
			"--heading-color": "#FFFFFF",
			"--icon-fill": "#FFFFFF",
			"--text-muted": "#E6EEE6",

			"--btn-default-bg": "#2B2E2B",
			"--btn-default-text-color": "#FFFFFF",

			"--chart-axis-label-color": "#FFFFFF",
			"--chart-grid-line-color": "rgba(255, 255, 255, 0.15)",

			"--checkbox-color": "#2B5129",
			"--checkbox-gradient": "linear-gradient(180deg, #2B5129 -124.51%, #2B5129 100%)"
		}
		: {
			"--primary": "#2B5129",
			"--primary-color": "#2B5129",
			"--brand-color": "#2B5129",
			"--blue-500": "#2B5129",
			"--btn-primary": "#2B5129",
			"--btn-primary-text-color": "#FFFFFF",
			"--border-primary": "#2B5129",

			"--bg-color": "#FFFFFF",
			"--fg-color": "#FFFFFF",
			"--layout-bg": "#FFFFFF",
			"--card-bg": "#FFFFFF",

			"--sidebar-bg": "#F5F7F5",
			"--surface-gray-1": "#F5F7F5",
			"--control-bg": "#F5F7F5",

			"--text-color": "#1A1C1A",
			"--heading-color": "#1A1C1A",
			"--gray-500": "#4A4E4A",
			"--text-muted": "#4A4E4A",

			"--checkbox-color": "#2B5129",
			"--checkbox-gradient": "linear-gradient(180deg, #2B5129 -124.51%, #2B5129 100%)"
		};
	Object.keys(vars).forEach(function(k) { root.style.setProperty(k, vars[k], "important"); });
}

function watchThemeSwitch() {
	var observer = new MutationObserver(function(mutations) {
		for (var i = 0; i < mutations.length; i++) {
			if (mutations[i].attributeName === "data-theme" || mutations[i].attributeName === "data-theme-mode") {
				applyTheme();
				return;
			}
		}
	});
	observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "data-theme-mode"] });
}

if (document.readyState === "complete") {
	applyTheme();
	watchThemeSwitch();
} else {
	window.addEventListener("load", function() {
		applyTheme();
		watchThemeSwitch();
	});
}
