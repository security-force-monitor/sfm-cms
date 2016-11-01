CREATE OR REPLACE VIEW organization AS 
  SELECT 
    oo.uuid AS id,
    oon.value AS name,
    oa.value AS alias,
    oc.value AS classification,
    ood.value AS division_id,
    oofc.value AS first_cited,
    oolc.value AS last_cited
  FROM organization_organization AS oo
  LEFT JOIN organization_organizationname AS oon
    ON oo.id = oon.object_ref_id
  LEFT JOIN organization_organizationalias AS ooa
    ON oo.id = ooa.object_ref_id
  LEFT JOIN organization_alias AS oa
    ON ooa.value_id = oa.id
  LEFT JOIN organization_organizationclassification AS ooc
    ON oo.id = ooc.object_ref_id
  LEFT JOIN organization_classification AS oc
    ON ooc.value_id = oc.id
  LEFT JOIN organization_organizationdivisionid AS ood
    ON oo.id = ood.object_ref_id
  LEFT JOIN organization_organizationfirstcited AS oofc
    ON oo.id = oofc.object_ref_id
  LEFT JOIN organization_organizationlastcited AS oolc
    ON oo.id = oolc.object_ref_id
