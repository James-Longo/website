// Family filter update function - add this after toggleFilter function

async function updateFamilyFilters() {
    familyFilters.innerHTML = '<div class="filter-chip" style="cursor:default; background:transparent;">Loading...</div>';
    
    try {
        // Get all species
        const speciesResponse = await fetch('http://localhost:5000/api/suggest?q=');
        const allSpeciesData = await speciesResponse.json();

        // Build family -> species map
        const familyToSpecies = new Map();
        allSpeciesData.forEach(sp => {
            const family = sp.family || 'Unknown';
            if (!familyToSpecies.has(family)) {
                familyToSpecies.set(family, []);
            }
            familyToSpecies.get(family).push(sp.en);
        });

        // Count species per family (simple version - just count all species)
        const familyCounts = new Map();
        familyToSpecies.forEach((species, family) => {
            familyCounts.set(family, species.length);
        });

        // Sort by count
        const sortedFamilies = Array.from(familyCounts.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 20); // Top 20 families

        // Render chips
        familyFilters.innerHTML = '';
        sortedFamilies.forEach(([family, count]) => {
            const chip = document.createElement('div');
            chip.className = 'filter-chip';
            if (selectedFamilies.has(family)) chip.classList.add('active');
            chip.innerText = `${family} (${count})`;
            chip.onclick = () => {
                toggleFilter(selectedFamilies, family, chip);
                updateAvailableTypes();
            };
            familyFilters.appendChild(chip);
        });
    } catch (err) {
        console.error("Failed to load families", err);
        familyFilters.innerHTML = '<div class="filter-chip" style="cursor:default; background:transparent;">Error loading families</div>';
    }
}
