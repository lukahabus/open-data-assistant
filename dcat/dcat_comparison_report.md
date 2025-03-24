# SQL vs. LLM DCAT Metadata Analysis Comparison

## Query: Find datasets about education

### SQL-like Approach
Time: 0.50 seconds

Result:
```
            id                             title                                                                                                                                                                                                                                                         description                                            keywords                themes      issued    modified                   publisher  distribution_count distribution_formats
0  dataset-001  Geoportal visokoskolske ustanove  Dataset containing the locations of higher education institutions in Zagreb.\n        Contains 75 institutions with their geographical coordinates and metadata.\n        The dataset includes the name of each institution, its address, and precise coordinates.  education, university, college, zagreb, geospatial  education, geography  2023-01-16  2023-01-30  City of Zagreb - Geoportal                   1                  CSV
```

### LLM-based Approach
Time: 2.75 seconds

Result:
```
I found two datasets related to education in the Open Data Zagreb Catalog:

1. **Dataset: Geoportal visokoskolske ustanove**
   - Description: Contains the locations of higher education institutions in Zagreb.
   - Publisher: City of Zagreb - Geoportal
   - Keywords: education, university, college, zagreb, geospatial
   - Themes: education, geography
   - Spatial Coverage: Point coordinates [15.97, 45.81]
   - Distribution: Geoportal visokoskolske ustanove CSV

2. **Dataset: Zagreb Streets Dataset**
   - Description: Contains information about streets in Zagreb.
   - Publisher: City of Zagreb
   - Keywords: streets, zagreb, urban, city, infrastructure
   - Themes: infrastructure, urban planning
   - Spatial Coverage: Point coordinates [15.97, 45.81]
   - Distribution: Zagreb Streets CSV

If you need more specific information or have any other questions, feel free to ask!
```

---

## Query: Which datasets were modified after January 2023?

### SQL-like Approach
Time: 0.42 seconds

Result:
```
            id                             title                                                                                                                                                                                                                                                         description                                            keywords                          themes      issued    modified                   publisher  distribution_count distribution_formats
0  dataset-001  Geoportal visokoskolske ustanove  Dataset containing the locations of higher education institutions in Zagreb.\n        Contains 75 institutions with their geographical coordinates and metadata.\n        The dataset includes the name of each institution, its address, and precise coordinates.  education, university, college, zagreb, geospatial            education, geography  2023-01-16  2023-01-30  City of Zagreb - Geoportal                   1                  CSV
1  dataset-002            Zagreb Streets Dataset                        Dataset containing information about streets in Zagreb.\n        Contains 5477 streets with detailed information about each street,\n        including the street name, the person or entity it was named after, and historical information.        streets, zagreb, urban, city, infrastructure  infrastructure, urban planning  2023-01-16  2023-01-30              City of Zagreb                   1                  CSV
```

### LLM-based Approach
Time: 1.30 seconds

Result:
```
I don't have information on datasets modified after January 2023 in the Open Data Zagreb Catalog. If you have a specific dataset in mind or if you can provide more details, I can help you further. Alternatively, you may want to explore the datasets in the catalog to see if there are any recent updates.
```

---

## Query: Show me datasets related to streets in Zagreb

### SQL-like Approach
Time: 0.49 seconds

Result:
```
Empty DataFrame
Columns: [id, title, description, keywords, themes, issued, modified, publisher, distribution_count, distribution_formats]
Index: []
```

### LLM-based Approach
Time: 2.81 seconds

Result:
```
Here are some datasets related to streets in Zagreb:

1. **Zagreb Streets Dataset**
   - Description: Dataset containing information about streets in Zagreb. Contains 5477 streets with detailed information about each street, including the street name, the person or entity it was named after, and historical information.
   - Publisher: City of Zagreb
   - Spatial Coverage: Point coordinates [15.97, 45.81]
   - Distribution: [Zagreb Streets CSV](link_to_csv)

2. **Geoportal visokoskolske ustanove**
   - Description: Dataset containing the locations of higher education institutions in Zagreb. Contains 75 institutions with their geographical coordinates and metadata. Includes the name of each institution, its address, and precise coordinates.
   - Publisher: City of Zagreb - Geoportal
   - Spatial Coverage: Point coordinates [15.97, 45.81]
   - Distribution: [Geoportal visokoskolske ustanove CSV](link_to_csv)

If you need more information about any specific dataset or have any other questions, feel free to ask!
```

---

## Query: What datasets have geospatial information?

### SQL-like Approach
Time: 0.53 seconds

Result:
```
            id                             title                                                                                                                                                                                                                                                         description                                            keywords                themes      issued    modified                   publisher  distribution_count distribution_formats
0  dataset-001  Geoportal visokoskolske ustanove  Dataset containing the locations of higher education institutions in Zagreb.\n        Contains 75 institutions with their geographical coordinates and metadata.\n        The dataset includes the name of each institution, its address, and precise coordinates.  education, university, college, zagreb, geospatial  education, geography  2023-01-16  2023-01-30  City of Zagreb - Geoportal                   1                  CSV
```

### LLM-based Approach
Time: 2.49 seconds

Result:
```
The datasets that have geospatial information are:
1. Geoportal visokoskolske ustanove
   - Description: Dataset containing the locations of higher education institutions in Zagreb.
   - Publisher: City of Zagreb - Geoportal
   - Spatial Coverage: {'type': 'Point', 'coordinates': [15.97, 45.81]}
   - Keywords: education, university, college, zagreb, geospatial
   - Themes: education, geography
   - Distribution: Geoportal visokoskolske ustanove CSV (Format: CSV)

2. Zagreb Streets Dataset
   - Description: Dataset containing information about streets in Zagreb.
   - Publisher: City of Zagreb
   - Spatial Coverage: {'type': 'Point', 'coordinates': [15.97, 45.81]}
   - Keywords: streets, zagreb, urban, city, infrastructure
   - Themes: infrastructure, urban planning
   - Distribution: Zagreb Streets CSV (Format: CSV)

You can explore these datasets further for more detailed geospatial information.
```

---

## Query: Find datasets with PDF distributions

### SQL-like Approach
Time: 0.40 seconds

Result:
```
Empty DataFrame
Columns: [id, title, description, keywords, themes, issued, modified, publisher, distribution_count, distribution_formats]
Index: []
```

### LLM-based Approach
Time: 1.27 seconds

Result:
```
Currently, the datasets in the Open Data Zagreb Catalog do not have PDF distributions. The available distributions for the datasets are in CSV format. If you have any specific requirements or questions regarding the datasets or their distributions, feel free to ask for more information.
```

---

## Overall Comparison

Average SQL-like query time: 0.47 seconds
Average LLM-based query time: 2.12 seconds

### Advantages and Limitations

#### SQL-like Approach

Advantages:
- Faster execution time
- Precise and structured results
- Well-suited for queries with specific criteria

Limitations:
- Limited to explicit metadata fields
- Cannot understand semantic meaning beyond keywords
- Struggles with ambiguous or nuanced queries

#### LLM-based Approach

Advantages:
- Can understand semantic meaning and context
- Handles natural language and ambiguous queries well
- Can infer relationships and connections between datasets
- Provides explanatory and conversational responses

Limitations:
- Slower execution time
- May introduce inaccuracies or hallucinations
- Less precise for structured data retrieval