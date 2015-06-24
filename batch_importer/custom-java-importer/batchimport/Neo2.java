/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

import org.neo4j.batchimport.importer.ChunkerLineData;
import org.neo4j.batchimport.importer.CsvLineData;
import org.neo4j.batchimport.importer.RelType;
import org.neo4j.batchimport.importer.Type;
import org.neo4j.batchimport.index.MapDbCachingIndexProvider;
import org.neo4j.batchimport.utils.Config;
import org.neo4j.graphdb.DynamicLabel;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.index.IndexManager;
import org.neo4j.index.lucene.unsafe.batchinsert.LuceneBatchInserterIndexProvider;
import org.neo4j.unsafe.batchinsert.BatchInserter;
import org.neo4j.unsafe.batchinsert.BatchInserters;
import org.neo4j.unsafe.batchinsert.BatchInserterIndexProvider;
import org.neo4j.unsafe.batchinsert.BatchInserterIndex;

import java.io.*;
import java.util.*;
import java.util.zip.GZIPInputStream;

import static org.neo4j.index.impl.lucene.LuceneIndexImplementation.EXACT_CONFIG;
import static org.neo4j.index.impl.lucene.LuceneIndexImplementation.FULLTEXT_CONFIG;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import au.com.bytecode.opencsv.CSVReader;
//import org.neo4j.kernel.impl.util.FileUtils;
//import static sun.org.mozilla.javascript.internal.Context.exit;

/**
 *
 * @author anil
 */
public class Neo2 {

    public static void main(String[] args) throws FileNotFoundException, IOException {
        BatchInserter inserter = null;
        try {
            String storeDir = "/home/anil.gautam/Smarter.Codes/src/Universal_Item_Picker/batch_importer/target/graph.db/";
            //deleteDir(new File(storeDir));
            inserter = BatchInserters.inserter(storeDir);
            CSVReader readbuffer = new CSVReader(new FileReader("/home/anil.gautam/Smarter.Codes/src/Universal_Item_Picker/batch_importer/nodes.csv"), '\t', '"', 0);
            String strRead, relRead;
            Map nodes = new HashMap();
            String name = null, label = null, uid = null, type = null,
                    obtainable = null, command = null,
                    label_property = null, rel_type = null,
                    unit = null, value = null, param = null;
            String entity_list[] = null;
            Long start = null, end = null;
            int a = -1;
            String[] splitarray;
             while ((splitarray = readbuffer.readNext()) != null) {
                if (a >= 0) {
                    Map<String, Object> properties = new HashMap<>();
                    if (splitarray.length > 0) {
                        name = splitarray[0];
                        if (name != null && !name.isEmpty()) {
                            properties.put("name", name);
                        }
                    }
                    if (splitarray.length > 1) {
                        label = splitarray[1];
                    }
                    if (splitarray.length > 2) {
                        uid = splitarray[2];
                        if (uid != null && !uid.isEmpty()) {
                            properties.put("uid", uid);
                        }
                    }
                    if (splitarray.length > 3) {
                        type = splitarray[3];
                        if (type != null && !type.isEmpty()) {
                            properties.put("type", type);
                        }
                    }
                    if (splitarray.length > 4) {
                        obtainable = splitarray[4];
                        if (obtainable != null && !obtainable.isEmpty()) {
                            properties.put("obtainable", obtainable);
                        }
                    }
                    if (splitarray.length > 5) {
                        command = splitarray[5];
                        if (command != null && !command.isEmpty()) {
                            properties.put("command", command);
                        }
                    }
                    if (splitarray.length > 6) {
                        label_property = (String) splitarray[6];
                        if (label_property != null && !label_property.isEmpty()) {
                            properties.put("label_property", label_property);
                        }
                    }
                    if (splitarray.length > 7) {
                        entity_list = getArrayList(splitarray[7]);
                        if (entity_list.length > 0) {
                            properties.put("entity", entity_list);
                        }
                    }
                    String[] labels = label.split(",");
                    int labelCount = labels.length;
                    Label[] nodeLabels = new Label[labelCount];
                    for (int i = 0; i < labelCount; i++) {
                        nodeLabels[i] = DynamicLabel.label(labels[i]);
                    }
                    long node = inserter.createNode(properties, nodeLabels);
                    nodes.put(a, node);
                }
                a += 1;
            }
            BufferedReader readrelbuffer;
            CSVReader reader = new CSVReader(new FileReader("/home/anil.gautam/Smarter.Codes/src/Universal_Item_Picker/batch_importer/rels.csv"), '\t', '"', 0);
            int rel = -1;
            String[] splitarray2;
            while ((splitarray2 = reader.readNext()) != null) {
                if (splitarray2 != null) {
                    rel += 1;
                    if (splitarray2[0] != null && !splitarray2[0].isEmpty()) {
                        if (rel > 0) {
                            if (splitarray2.length > 0) {
                                start = Long.parseLong(splitarray2[0]);
                            }
                            if (splitarray2.length > 1) {
                                end = Long.parseLong(splitarray2[1]);
                            }
                            if (splitarray2.length > 2) {
                                rel_type = splitarray2[2];
                            }
                            if (splitarray2.length > 3) {
                                unit = splitarray2[3];
                            }
                            if (splitarray2.length > 4) {
                                value = splitarray2[4];
                            }
                            if (splitarray2.length > 5) {
                                param = splitarray2[5];
                            }
                            final RelType relType = new RelType();
                            final RelType knows = relType.update(rel_type);
//                        RelationshipType knows = DynamicRelationshipType.withName(rel_type);
                            Map<String, Object> properties = new HashMap<>();
                            if (value != null && !value.isEmpty()) {
                                properties.put("value", value);
                            }
                            if (unit != null && !unit.isEmpty()) {
                                properties.put("unit", unit);
                            }
                            if (param != null && !param.isEmpty()) {
                                properties.put("param", param);
                            }
                            if (properties.size() == 0) {
                                properties = null;
                            }
                            Map<String, Object> start_properties = new HashMap<>();
                            Map<String, Object> end_properties = new HashMap<>();
                            start_properties = inserter.getNodeProperties(start);
//                        System.out.println("end is "+end);
                            end_properties = inserter.getNodeProperties(end);
//                        System.out.println(start_properties);
//                        System.out.println(end_properties);
                            if (start_properties.size() > 0 && end_properties.size() > 0) {
                                inserter.createRelationship(start, end, knows, properties);
                            }
                        }
                    }
                }
            }
        } finally {
            if (inserter != null) {
                inserter.shutdown();
            }

        }
    }

    public static String[] getArrayList(String test_string) {
        String[] labels = test_string.split(",");
        int labelCount = labels.length;
        String[] nodeLabels = new String[labelCount];
        for (int i = 0; i < labelCount; i++) {
            labels[i] = labels[i];
        }
        return labels;
    }

    public static boolean deleteDir(File dir) {
        if (dir.isDirectory()) {
            String[] children = dir.list();
            for (int i = 0; i < children.length; i++) {
                boolean success = deleteDir(new File(dir, children[i]));
                if (!success) {
                    return false;
                }
            }
        }
        return dir.delete();
    }
}

