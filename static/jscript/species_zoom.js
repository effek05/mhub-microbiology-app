const vaccineData = {
  Debaryomyces: {
    title: 'Debaryomyces hansenii',
    orga: 'yeast',
    p: 'pathogenic',
    orig: 'cheese',
    body: "Debaryomyces hansenii is a species of yeast. It accounts for up to 2% of invasive candidiasis cases (fungal infection) and is being investigated as the environmental trigger of Crohn's disease (chronic bowel inflamation). This is caused by toxins, which it produces to destroy competitive yeast species. Some strains have been researched for potential use as probiotics as they may have health benefits. It is a common species in all types of cheese, including soft cheeses and the brines of semi-hard and hard cheeses, and the most common yeast in sausages."
  },
  Leucobacter: {
    title: 'Leucobacter',
    orga: 'bacterium',
    p: 'several',
    orig: 'cheese',
    body: "Leucobacter is a genus (group of species, e.g. small cats) of 25 species of rod-shaped bacteria. It has been found globally in water and on land. They span an extremely diverse niche of free-living and host-associated ecosystems. In some host, they are a parasite, in others they act as protection. Have been found on the rind of cheeses, though their function in ripening has not been found out."
  },
  Yarrowia: {
    title: 'Yarrowia lipolytica',
    orga: 'yeast',
    p: 'non-pathogenic',
    orig: 'cheese',
    body: "Y. lipolytica are a species of fungus which can produce special lipids (e.g. vitamins) from usually unused carbon sources. This makes them interesting for industrial applications. It has been found in many different places where these lipids are present, for instance milled corn fiber tailings or Paris sewers. Yarrowia lipolytica requires oxygen to live (strictly aerobic). Depending on the environment, they form two different phenotypes (appearance). The usual one is round/sperical, but under stree they form hyphae (long, branching filaments). In itself, it is not harmful, only a rare opportunistic pathogen, as it may cause infections in patitents with weaker immune systems."
  },
  Geotrichum: {
    title: 'Geotrichum candidum',
    orga: 'yeast',
    p: 'pathogenic',
    orig: 'cheese',
    body: "This is a fungus, which can also be found as part if the human microbiome, our skin, mucus, and feces. It is present in every third/fourth human. It is also common in soil and has been isolated from all continents. In humans, it can cause the disease geotrichosis and in plants sour rot, affecting citrus fruits, tomatoes, carrots, and other vegetables. Nevertheless, it is widely used in the production of certain dairy products, like many cheeses and yoghurt. The species was first discovered on decaying leaves."
  },
  Arthrobacter: {
    title: 'Arthrobacter arilaitensis',
    orga: 'bacterium',
    p: 'non-pathogenic',
    orig: 'cheese',
    body: "This microbe is also known as Glutamicibacter arilaitensis. It was isolated from cheese, especially smear-ripened ones. A./G. arilaitensis is able to metabolize fatty acids, amino acids and lactic acid. Generally, it contributes to the typical flavouring, colour and texture of the cheese."
  },
  Hafnia: {
    title: 'Hafnia alvei',
    orga: 'bacterium',
    p: 'non-pathogenic',
    orig: 'cheese',
    body: "Hafnia alvei is a rod-shaped bacteria, which is facultatively anaerobic (can survive without oxygen). It is a commensal (positive effects for both partners) of the human gastrointestinal tract and not normally pathogenic. Only in immunocompromised patients (already weakened immune system), might it lead to a disease. Unfortunately, it's often resistant to multiple antibiotics, and as with many other bacteria, this will be a problem in the near future. The name comes from Hafnia, the Latin name for Copenhagen. It can also be used as a lactic fermenter for the dairy industry and, more recently, as a probiotic included in a dietary supplement product. In the ripening of raw milk cheese, H. alvei is one of the dominant species and found in raw milk itself."
  },
  Corynebacterium: {
    title: 'Corynebacterium casei',
    orga: 'bacterium',
    p: 'non-pathogenic',
    orig: 'cheese',
    body: "Bacteria from the genus Corynebacterium were isolated from samples of a smear-ripened cheese around 2000. Following this, scientist did phylogenetic analysis (how they are genetically in relation to each other). Through this, they discovered two new strains, including Corynebacterium casei. This was done, e.g. with DNA-DNA hybridization, a technique to compare how similar the genetic material of microbes is, based on how stable aligning fragments of this is. All found Corynebacterium bacteria are non-spore forming rods, meaning they cannot go from there natural rod-shaped phenotype to a more resilient spore."
  },
  Brevibacterium: {
    title: 'Brevibacterium aurantiacum',
    orga: 'bacterium',
    p: 'non-pathogenic',
    orig: 'cheese',
    body: "B. aurantiacum is part of the genus Brevibacterium, which is often use to produce cheese and amino acids (protein building blocks). They are not able to move on their own (non-motile), need oxygen to survive (obligate aerobes) and use carbon precursors for energy and provision of carbon molecules itself (chemoorganotrophs). Their genetic material is DNA with a high content of GC (guanine-cytosine), making the two strands harder to separate. Between publications, the name might differ and many Brevibacterium species have been assigned to other genera in the past. "
  },
  Staphylococcus: {
    title: 'Staphylococcus xylosus',
    orga: 'bacterium',
    p: 'non-pathogenic',
    orig: 'cheese',
    body: "Staphylococcus xylosus is a species of bacteria that forms clusters of cells. For that, they produce a slime, but this ability is lost upon subculture (). It is a commensal (positive effect) on the skin of humans and animals, where the second one is more common. It is also used in salami fermentation. In the past, patients of been diagnosed with an infection of S. xylosus, but this is often regarded as a misidentification later on. Fortunately, it is still sensitive to several antibiotics, including penicillin and erythromycin. "
  }
};

function openModal(id) {
  const v = vaccineData[id];
  if (!v) return;
  let html = `<h2 class="modal-title">${v.title}</h2>
              <p><span class="tag org">${v.orga}</span> <span class="tag p">${v.p}</span> <span class="tag orig">${v.orig}</span></p>
              <div class="modal-body">${v.body}</div>`;
  document.getElementById('modal-content').innerHTML = html;
  document.getElementById('modal-overlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal(e) {
  if (e.target === document.getElementById('modal-overlay')) {
    document.getElementById('modal-overlay').classList.remove('active');
    document.body.style.overflow = '';
  }
}

function closeModalBtn() {
  document.getElementById('modal-overlay').classList.remove('active');
  document.body.style.overflow = '';
}


