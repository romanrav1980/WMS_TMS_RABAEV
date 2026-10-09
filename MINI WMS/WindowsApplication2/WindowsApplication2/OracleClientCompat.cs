using System;
using System.Data;
using Oracle.ManagedDataAccess.Client;
using ManagedTypes = Oracle.ManagedDataAccess.Types;

namespace System.Data.OracleClient
{
    public enum OracleType
    {
        Char,
        DateTime,
        Int16,
        Int32,
        Number,
        Timestamp,
        UInt16,
        UInt32,
        VarChar
    }

    internal static class OracleTypeMapper
    {
        internal static OracleDbType Map(OracleType oracleType)
        {
            switch (oracleType)
            {
                case OracleType.Char:
                    return OracleDbType.Char;
                case OracleType.DateTime:
                    return OracleDbType.Date;
                case OracleType.Int16:
                    return OracleDbType.Int16;
                case OracleType.Int32:
                    return OracleDbType.Int32;
                case OracleType.Number:
                    return OracleDbType.Decimal;
                case OracleType.Timestamp:
                    return OracleDbType.TimeStamp;
                case OracleType.UInt16:
                    return OracleDbType.Int32;
                case OracleType.UInt32:
                    return OracleDbType.Int64;
                case OracleType.VarChar:
                default:
                    return OracleDbType.Varchar2;
            }
        }
    }

    internal static class OracleValueMapper
    {
        internal static object ToLegacyValue(object value)
        {
            if (value == null || value is DBNull)
            {
                return value;
            }

            if (value is ManagedTypes.OracleDecimal)
            {
                ManagedTypes.OracleDecimal decimalValue = (ManagedTypes.OracleDecimal)value;
                return decimalValue.IsNull ? null : (object)decimalValue.Value;
            }

            if (value is ManagedTypes.OracleString)
            {
                ManagedTypes.OracleString stringValue = (ManagedTypes.OracleString)value;
                return stringValue.IsNull ? null : (object)stringValue.Value;
            }

            if (value is ManagedTypes.OracleDate)
            {
                ManagedTypes.OracleDate dateValue = (ManagedTypes.OracleDate)value;
                return dateValue.IsNull ? null : (object)dateValue.Value;
            }

            if (value is ManagedTypes.OracleTimeStamp)
            {
                ManagedTypes.OracleTimeStamp timestampValue = (ManagedTypes.OracleTimeStamp)value;
                return timestampValue.IsNull ? null : (object)timestampValue.Value;
            }

            if (value is ManagedTypes.OracleTimeStampLTZ)
            {
                ManagedTypes.OracleTimeStampLTZ timestampValue = (ManagedTypes.OracleTimeStampLTZ)value;
                return timestampValue.IsNull ? null : (object)timestampValue.Value;
            }

            if (value is ManagedTypes.OracleTimeStampTZ)
            {
                ManagedTypes.OracleTimeStampTZ timestampValue = (ManagedTypes.OracleTimeStampTZ)value;
                return timestampValue.IsNull ? null : (object)timestampValue.Value;
            }

            if (value is ManagedTypes.OracleBlob)
            {
                ManagedTypes.OracleBlob blobValue = (ManagedTypes.OracleBlob)value;
                return blobValue.IsNull ? null : (object)blobValue.Value;
            }

            if (value is ManagedTypes.OracleBinary)
            {
                ManagedTypes.OracleBinary binaryValue = (ManagedTypes.OracleBinary)value;
                return binaryValue.IsNull ? null : (object)binaryValue.Value;
            }

            if (value is ManagedTypes.OracleClob)
            {
                ManagedTypes.OracleClob clobValue = (ManagedTypes.OracleClob)value;
                return clobValue.IsNull ? null : (object)clobValue.Value;
            }

            return value;
        }

        internal static object ToManagedValue(object value)
        {
            OracleString oracleString = value as OracleString;
            if (oracleString != null)
            {
                return oracleString.Inner;
            }

            OracleNumber oracleNumber = value as OracleNumber;
            if (oracleNumber != null)
            {
                return oracleNumber.Inner;
            }

            return value;
        }
    }

    public sealed class OracleString
    {
        internal readonly ManagedTypes.OracleString Inner;

        internal OracleString(ManagedTypes.OracleString inner)
        {
            Inner = inner;
        }

        public bool IsNull
        {
            get { return Inner.IsNull; }
        }

        public string Value
        {
            get { return Inner.Value; }
        }

        public override string ToString()
        {
            return Inner.ToString();
        }
    }

    public sealed class OracleNumber
    {
        internal readonly ManagedTypes.OracleDecimal Inner;

        internal OracleNumber(ManagedTypes.OracleDecimal inner)
        {
            Inner = inner;
        }

        public bool IsNull
        {
            get { return Inner.IsNull; }
        }

        public decimal Value
        {
            get { return Inner.Value; }
        }

        public override string ToString()
        {
            return Inner.ToString();
        }
    }

    public sealed class OracleParameter
    {
        internal readonly Oracle.ManagedDataAccess.Client.OracleParameter Inner;

        internal OracleParameter(Oracle.ManagedDataAccess.Client.OracleParameter inner)
        {
            Inner = inner;
        }

        public object Value
        {
            get { return OracleValueMapper.ToLegacyValue(Inner.Value); }
            set { Inner.Value = OracleValueMapper.ToManagedValue(value); }
        }

        public ParameterDirection Direction
        {
            get { return Inner.Direction; }
            set { Inner.Direction = value; }
        }
    }

    public sealed class OracleParameterCollection
    {
        private readonly Oracle.ManagedDataAccess.Client.OracleParameterCollection inner;

        internal OracleParameterCollection(Oracle.ManagedDataAccess.Client.OracleParameterCollection inner)
        {
            this.inner = inner;
        }

        public OracleParameter Add(string parameterName, OracleType oracleType)
        {
            return new OracleParameter(inner.Add(parameterName, OracleTypeMapper.Map(oracleType)));
        }

        public OracleParameter Add(string parameterName, OracleType oracleType, int size)
        {
            return new OracleParameter(inner.Add(parameterName, OracleTypeMapper.Map(oracleType), size));
        }

        public OracleParameter this[string parameterName]
        {
            get { return new OracleParameter(inner[parameterName]); }
        }
    }

    public sealed class OracleConnection : IDisposable
    {
        internal readonly Oracle.ManagedDataAccess.Client.OracleConnection Inner;

        public OracleConnection()
        {
            Inner = new Oracle.ManagedDataAccess.Client.OracleConnection();
        }

        internal OracleConnection(Oracle.ManagedDataAccess.Client.OracleConnection inner)
        {
            Inner = inner;
        }

        public string ConnectionString
        {
            get { return Inner.ConnectionString; }
            set { Inner.ConnectionString = value; }
        }

        public ConnectionState State
        {
            get { return Inner.State; }
        }

        public void Open()
        {
            Inner.Open();
        }

        public void Close()
        {
            Inner.Close();
        }

        public void Dispose()
        {
            Inner.Dispose();
        }
    }

    public sealed class OracleCommand : IDisposable
    {
        private readonly OracleParameterCollection parameters;
        private OracleConnection connection;

        internal readonly Oracle.ManagedDataAccess.Client.OracleCommand Inner;

        public OracleCommand()
        {
            Inner = new Oracle.ManagedDataAccess.Client.OracleCommand();
            parameters = new OracleParameterCollection(Inner.Parameters);
        }

        public OracleConnection Connection
        {
            get { return connection; }
            set
            {
                connection = value;
                Inner.Connection = value == null ? null : value.Inner;
            }
        }

        public string CommandText
        {
            get { return Inner.CommandText; }
            set { Inner.CommandText = value; }
        }

        public CommandType CommandType
        {
            get { return Inner.CommandType; }
            set { Inner.CommandType = value; }
        }

        public OracleParameterCollection Parameters
        {
            get { return parameters; }
        }

        public OracleDataReader ExecuteReader()
        {
            NormalizeStoredProcedureParameters();
            return new OracleDataReader(Inner.ExecuteReader());
        }

        public int ExecuteNonQuery()
        {
            NormalizeStoredProcedureParameters();
            return Inner.ExecuteNonQuery();
        }

        public object ExecuteScalar()
        {
            NormalizeStoredProcedureParameters();
            return OracleValueMapper.ToLegacyValue(Inner.ExecuteScalar());
        }

        public object ExecuteOracleScalar()
        {
            NormalizeStoredProcedureParameters();
            return OracleValueMapper.ToLegacyValue(Inner.ExecuteScalar());
        }

        private void NormalizeStoredProcedureParameters()
        {
            if (Inner.CommandType != CommandType.StoredProcedure || Inner.Parameters.Count <= 1)
            {
                return;
            }

            int returnParameterIndex = -1;
            for (int i = 0; i < Inner.Parameters.Count; i++)
            {
                if (Inner.Parameters[i].Direction == ParameterDirection.ReturnValue)
                {
                    returnParameterIndex = i;
                    break;
                }
            }

            if (returnParameterIndex <= 0)
            {
                return;
            }

            Oracle.ManagedDataAccess.Client.OracleParameter returnParameter = Inner.Parameters[returnParameterIndex];
            Inner.Parameters.RemoveAt(returnParameterIndex);
            Inner.Parameters.Insert(0, returnParameter);
        }

        public void Dispose()
        {
            Inner.Dispose();
        }
    }

    public sealed class OracleDataReader : IDisposable
    {
        private readonly Oracle.ManagedDataAccess.Client.OracleDataReader inner;

        internal OracleDataReader(Oracle.ManagedDataAccess.Client.OracleDataReader inner)
        {
            this.inner = inner;
        }

        public int FieldCount
        {
            get { return inner.FieldCount; }
        }

        public int VisibleFieldCount
        {
            get { return inner.VisibleFieldCount; }
        }

        public bool Read()
        {
            return inner.Read();
        }

        public string GetName(int i)
        {
            return inner.GetName(i);
        }

        public object GetValue(int i)
        {
            return OracleValueMapper.ToLegacyValue(inner.GetValue(i));
        }

        public string GetString(int i)
        {
            return inner.GetString(i);
        }

        public double GetDouble(int i)
        {
            return inner.GetDouble(i);
        }

        public DateTime GetDateTime(int i)
        {
            return inner.GetDateTime(i);
        }

        public int GetInt32(int i)
        {
            return inner.GetInt32(i);
        }

        public float GetFloat(int i)
        {
            return inner.GetFloat(i);
        }

        public OracleString GetOracleString(int i)
        {
            return new OracleString(inner.GetOracleString(i));
        }

        public OracleNumber GetOracleNumber(int i)
        {
            return new OracleNumber(inner.GetOracleDecimal(i));
        }

        public object GetOracleValue(int i)
        {
            return OracleValueMapper.ToLegacyValue(inner.GetOracleValue(i));
        }

        public void Close()
        {
            inner.Close();
        }

        public void Dispose()
        {
            inner.Dispose();
        }
    }
}
